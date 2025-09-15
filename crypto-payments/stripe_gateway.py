"""
Stripe Payment Gateway Integration for Mycelium-EI-Lang
Traditional credit card payments alongside cryptocurrency options
"""

import stripe
import os
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded" 
    FAILED = "failed"
    CANCELED = "canceled"
    REQUIRES_ACTION = "requires_action"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"

@dataclass
class PricingTier:
    name: str
    stripe_price_id: str
    usd_monthly: float
    usd_yearly: float
    stripe_discount: float  # Credit card processing fee offset
    features: List[str]
    api_calls: int
    support_level: str

class MyceliumStripeGateway:
    """Stripe payment integration for traditional card payments"""
    
    # Stripe Price IDs (need to be created in Stripe dashboard)
    PRICING_TIERS = {
        "community": PricingTier(
            name="Community",
            stripe_price_id="price_community_free",  # Free tier
            usd_monthly=0.0,
            usd_yearly=0.0,
            stripe_discount=0.0,
            features=["Basic bio-algorithms", "Community support"],
            api_calls=1000,
            support_level="community"
        ),
        "professional": PricingTier(
            name="Professional",
            stripe_price_id="price_professional_monthly",
            usd_monthly=299.0,
            usd_yearly=2999.0,  # 2 months free
            stripe_discount=0.05,  # 5% off to offset processing fees
            features=["Commercial algorithms", "Priority support", "GPU acceleration"],
            api_calls=100000,
            support_level="priority"
        ),
        "enterprise": PricingTier(
            name="Enterprise", 
            stripe_price_id="price_enterprise_monthly",
            usd_monthly=2999.0,
            usd_yearly=29999.0,  # 2 months free
            stripe_discount=0.08,  # 8% off to offset processing fees
            features=["Unlimited algorithms", "Dedicated support", "Custom integrations"],
            api_calls=10000000,
            support_level="dedicated"
        ),
        "quantum": PricingTier(
            name="Quantum",
            stripe_price_id="price_quantum_monthly", 
            usd_monthly=9999.0,
            usd_yearly=99999.0,  # 2 months free
            stripe_discount=0.10,  # 10% off to offset processing fees  
            features=["Quantum computing", "White-label licensing", "Research partnerships"],
            api_calls=-1,  # Unlimited
            support_level="white-glove"
        )
    }
    
    def __init__(self, api_key: str, webhook_secret: Optional[str] = None):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        stripe.api_key = api_key
        
    def create_subscription_checkout(self, 
                                   plan: str,
                                   customer_email: str,
                                   billing_cycle: str = "monthly",
                                   success_url: str = None,
                                   cancel_url: str = None) -> Dict:
        """Create Stripe Checkout session for subscription"""
        
        if plan not in self.PRICING_TIERS:
            return {"error": f"Invalid plan: {plan}"}
        
        tier = self.PRICING_TIERS[plan]
        
        # Community plan is free - no payment needed
        if plan == "community":
            return {
                "success": True,
                "message": "Community plan activated - no payment required",
                "plan": plan
            }
        
        # Determine price ID based on billing cycle
        price_id = tier.stripe_price_id
        if billing_cycle == "yearly":
            price_id = price_id.replace("_monthly", "_yearly")
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=customer_email,
                success_url=success_url or f"https://mycelium-ei-lang.com/success?plan={plan}",
                cancel_url=cancel_url or "https://mycelium-ei-lang.com/cancel",
                metadata={
                    "plan": plan,
                    "billing_cycle": billing_cycle,
                    "platform": "mycelium-ei-lang"
                },
                subscription_data={
                    "metadata": {
                        "plan": plan,
                        "billing_cycle": billing_cycle
                    }
                },
                # Apply discount for Stripe processing fees
                discounts=[{
                    "coupon": f"stripe_discount_{plan}"  # Create in Stripe dashboard
                }] if tier.stripe_discount > 0 else None
            )
            
            return {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "plan": plan,
                "billing_cycle": billing_cycle,
                "amount": tier.usd_yearly if billing_cycle == "yearly" else tier.usd_monthly,
                "discount_percent": tier.stripe_discount * 100
            }
            
        except stripe.error.StripeError as e:
            return {"error": f"Stripe error: {str(e)}"}
    
    def create_credits_checkout(self,
                              credits_amount: int,
                              customer_email: str,
                              success_url: str = None,
                              cancel_url: str = None) -> Dict:
        """Create one-time payment for compute credits"""
        
        credit_price = 0.10  # $0.10 per credit
        total_amount = credits_amount * credit_price
        
        # Apply bulk discounts
        if credits_amount >= 1000:
            discount = 0.20  # 20% discount
        elif credits_amount >= 500:
            discount = 0.15  # 15% discount
        elif credits_amount >= 100:
            discount = 0.10  # 10% discount
        else:
            discount = 0.0
        
        final_amount = total_amount * (1 - discount)
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Mycelium Compute Credits - {credits_amount:,} credits',
                            'description': f'Bio-algorithm computation credits',
                        },
                        'unit_amount': int(final_amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                customer_email=customer_email,
                success_url=success_url or "https://mycelium-ei-lang.com/credits/success",
                cancel_url=cancel_url or "https://mycelium-ei-lang.com/credits/cancel",
                metadata={
                    "type": "compute_credits",
                    "credits_amount": str(credits_amount),
                    "credit_price": str(credit_price),
                    "original_amount": str(total_amount),
                    "discount_percent": str(discount * 100),
                    "final_amount": str(final_amount)
                }
            )
            
            return {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "credits_amount": credits_amount,
                "original_amount": total_amount,
                "discount_percent": discount * 100,
                "final_amount": final_amount,
                "savings": total_amount - final_amount
            }
            
        except stripe.error.StripeError as e:
            return {"error": f"Stripe error: {str(e)}"}
    
    def get_subscription_status(self, subscription_id: str) -> Dict:
        """Get subscription details and status"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan": subscription.metadata.get("plan"),
                "billing_cycle": subscription.metadata.get("billing_cycle"),
                "customer": subscription.customer
            }
            
        except stripe.error.StripeError as e:
            return {"error": f"Stripe error: {str(e)}"}
    
    def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Dict:
        """Cancel subscription"""
        try:
            if immediately:
                subscription = stripe.Subscription.cancel(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": subscription.canceled_at
            }
            
        except stripe.error.StripeError as e:
            return {"error": f"Stripe error: {str(e)}"}
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        if not self.webhook_secret:
            return False
        
        try:
            stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return True
        except (ValueError, stripe.error.SignatureVerificationError):
            return False
    
    def process_webhook(self, payload: bytes, signature: str) -> Dict:
        """Process Stripe webhook events"""
        if not self.verify_webhook_signature(payload, signature):
            return {"error": "Invalid webhook signature"}
        
        try:
            event = stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            
            if event['type'] == 'checkout.session.completed':
                return self._handle_checkout_completed(event['data']['object'])
            elif event['type'] == 'customer.subscription.created':
                return self._handle_subscription_created(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            else:
                return {"message": f"Unhandled event type: {event['type']}"}
                
        except Exception as e:
            return {"error": f"Webhook processing failed: {str(e)}"}
    
    def _handle_checkout_completed(self, session) -> Dict:
        """Handle successful checkout completion"""
        if session['mode'] == 'payment':
            # One-time payment (compute credits)
            metadata = session['metadata']
            return {
                "action": "add_compute_credits",
                "customer_email": session['customer_details']['email'],
                "credits_amount": int(metadata.get('credits_amount', 0)),
                "amount_paid": session['amount_total'] / 100,
                "session_id": session['id']
            }
        elif session['mode'] == 'subscription':
            # Subscription payment
            metadata = session['metadata']
            return {
                "action": "activate_subscription",
                "customer_email": session['customer_details']['email'],
                "plan": metadata.get('plan'),
                "billing_cycle": metadata.get('billing_cycle'),
                "subscription_id": session['subscription'],
                "session_id": session['id']
            }
        
        return {"message": "Checkout completed but no action defined"}
    
    def _handle_subscription_created(self, subscription) -> Dict:
        """Handle new subscription creation"""
        return {
            "action": "subscription_activated",
            "subscription_id": subscription['id'],
            "customer": subscription['customer'],
            "plan": subscription['metadata'].get('plan'),
            "status": subscription['status']
        }
    
    def _handle_subscription_updated(self, subscription) -> Dict:
        """Handle subscription updates"""
        return {
            "action": "subscription_updated",
            "subscription_id": subscription['id'],
            "status": subscription['status'],
            "cancel_at_period_end": subscription['cancel_at_period_end']
        }
    
    def _handle_subscription_deleted(self, subscription) -> Dict:
        """Handle subscription cancellation"""
        return {
            "action": "subscription_canceled", 
            "subscription_id": subscription['id'],
            "customer": subscription['customer'],
            "canceled_at": subscription['canceled_at']
        }
    
    def _handle_payment_failed(self, invoice) -> Dict:
        """Handle failed payment"""
        return {
            "action": "payment_failed",
            "subscription_id": invoice['subscription'],
            "customer": invoice['customer'],
            "amount_due": invoice['amount_due'] / 100,
            "attempt_count": invoice['attempt_count']
        }
    
    def create_stripe_products(self) -> Dict:
        """Helper method to create Stripe products and prices (run once)"""
        results = {}
        
        for plan_key, tier in self.PRICING_TIERS.items():
            if plan_key == "community":
                continue  # Skip free tier
                
            try:
                # Create product
                product = stripe.Product.create(
                    name=f"Mycelium-EI-Lang {tier.name}",
                    description=f"{tier.name} subscription - {', '.join(tier.features)}"
                )
                
                # Create monthly price
                monthly_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(tier.usd_monthly * 100),  # Convert to cents
                    currency='usd',
                    recurring={'interval': 'month'},
                    metadata={'plan': plan_key, 'billing_cycle': 'monthly'}
                )
                
                # Create yearly price
                yearly_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(tier.usd_yearly * 100),  # Convert to cents
                    currency='usd',
                    recurring={'interval': 'year'},
                    metadata={'plan': plan_key, 'billing_cycle': 'yearly'}
                )
                
                # Create discount coupon
                coupon = stripe.Coupon.create(
                    percent_off=tier.stripe_discount * 100,
                    duration='forever',
                    id=f'stripe_discount_{plan_key}',
                    name=f'{tier.name} Stripe Processing Discount'
                )
                
                results[plan_key] = {
                    "product_id": product.id,
                    "monthly_price_id": monthly_price.id,
                    "yearly_price_id": yearly_price.id,
                    "coupon_id": coupon.id
                }
                
            except stripe.error.StripeError as e:
                results[plan_key] = {"error": str(e)}
        
        return results
    
    def get_pricing_summary(self) -> Dict:
        """Get pricing summary for frontend display"""
        pricing = {}
        
        for plan_key, tier in self.PRICING_TIERS.items():
            pricing[plan_key] = {
                "name": tier.name,
                "monthly_price": tier.usd_monthly,
                "yearly_price": tier.usd_yearly,
                "yearly_savings": (tier.usd_monthly * 12) - tier.usd_yearly,
                "stripe_discount": tier.stripe_discount * 100,
                "features": tier.features,
                "api_calls": tier.api_calls,
                "support_level": tier.support_level
            }
        
        return pricing


# Usage example and testing
if __name__ == "__main__":
    # Initialize with test API key
    test_api_key = os.getenv("STRIPE_TEST_SECRET_KEY", "sk_test_...")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    gateway = MyceliumStripeGateway(test_api_key, webhook_secret)
    
    # Example: Create professional subscription checkout
    checkout = gateway.create_subscription_checkout(
        plan="professional",
        customer_email="user@example.com",
        billing_cycle="monthly"
    )
    
    print("Subscription Checkout:")
    print(json.dumps(checkout, indent=2))
    
    # Example: Create compute credits checkout
    credits_checkout = gateway.create_credits_checkout(
        credits_amount=500,
        customer_email="user@example.com"
    )
    
    print("\nCompute Credits Checkout:")
    print(json.dumps(credits_checkout, indent=2))
    
    # Example: Get pricing summary
    pricing = gateway.get_pricing_summary()
    print("\nPricing Summary:")
    print(json.dumps(pricing, indent=2))