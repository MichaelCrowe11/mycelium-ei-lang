"""
Mycelium-EI-Lang Coinbase Commerce Payment Gateway
Handles cryptocurrency payments for bio-computing subscriptions
"""

import os
import json
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed" 
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class SubscriptionPlan(Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

@dataclass
class PricingTier:
    name: str
    usd_price: float
    crypto_discount: float
    features: List[str]
    api_calls: int
    support_level: str

class MyceliumPaymentGateway:
    """Coinbase Commerce integration for Mycelium-EI-Lang payments"""
    
    PRICING_TIERS = {
        SubscriptionPlan.COMMUNITY: PricingTier(
            name="Community",
            usd_price=0.0,
            crypto_discount=0.0,
            features=["Basic bio-algorithms", "Community support"],
            api_calls=1000,
            support_level="community"
        ),
        SubscriptionPlan.PROFESSIONAL: PricingTier(
            name="Professional", 
            usd_price=299.0,
            crypto_discount=0.10,
            features=["Commercial algorithms", "Priority support", "GPU acceleration"],
            api_calls=100000,
            support_level="priority"
        ),
        SubscriptionPlan.ENTERPRISE: PricingTier(
            name="Enterprise",
            usd_price=2999.0, 
            crypto_discount=0.15,
            features=["Unlimited algorithms", "Dedicated support", "Custom integrations"],
            api_calls=10000000,
            support_level="dedicated"
        ),
        SubscriptionPlan.QUANTUM: PricingTier(
            name="Quantum",
            usd_price=9999.0,
            crypto_discount=0.20,
            features=["Quantum computing", "White-label licensing", "Research partnerships"],
            api_calls=-1,  # Unlimited
            support_level="white-glove"
        )
    }
    
    SUPPORTED_CRYPTOCURRENCIES = {
        "BTC": {"name": "Bitcoin", "symbol": "₿"},
        "ETH": {"name": "Ethereum", "symbol": "Ξ"},
        "USDC": {"name": "USD Coin", "symbol": "$"},
        "MATIC": {"name": "Polygon", "symbol": "♦"},
        "SOL": {"name": "Solana", "symbol": "◎"},
        "LINK": {"name": "Chainlink", "symbol": "🔗"}
    }
    
    def __init__(self, api_key: str, webhook_secret: Optional[str] = None):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.base_url = "https://api.commerce.coinbase.com"
        self.headers = {
            "Content-Type": "application/json",
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22"
        }
    
    def create_subscription_payment(self, 
                                  plan: SubscriptionPlan,
                                  user_id: str,
                                  duration_months: int = 1,
                                  user_email: Optional[str] = None) -> Dict:
        """Create a cryptocurrency payment for subscription"""
        
        tier = self.PRICING_TIERS[plan]
        
        # Calculate pricing with crypto discount
        base_price = tier.usd_price * duration_months
        discounted_price = base_price * (1 - tier.crypto_discount)
        
        # Create payment charge
        charge_data = {
            "name": f"Mycelium-EI-Lang {tier.name} Subscription",
            "description": f"{tier.name} plan for {duration_months} month(s) - Bio-computing platform",
            "local_price": {
                "amount": f"{discounted_price:.2f}",
                "currency": "USD"
            },
            "pricing_type": "fixed_price",
            "metadata": {
                "user_id": user_id,
                "plan": plan.value,
                "duration_months": str(duration_months),
                "original_price": f"{base_price:.2f}",
                "discount_applied": f"{tier.crypto_discount:.2f}",
                "api_calls_limit": str(tier.api_calls),
                "features": json.dumps(tier.features)
            },
            "redirect_url": f"https://mycelium-ei-lang.com/payment/success?plan={plan.value}",
            "cancel_url": f"https://mycelium-ei-lang.com/payment/cancel"
        }
        
        if user_email:
            charge_data["metadata"]["user_email"] = user_email
        
        try:
            response = requests.post(
                f"{self.base_url}/charges",
                headers=self.headers,
                json=charge_data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Add additional metadata for frontend
            if "data" in result:
                result["data"]["pricing_info"] = {
                    "plan_name": tier.name,
                    "original_price": base_price,
                    "discounted_price": discounted_price,
                    "crypto_discount": tier.crypto_discount * 100,
                    "savings": base_price - discounted_price
                }
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Payment creation failed: {str(e)}"}
    
    def create_compute_credits_payment(self, 
                                     credits_amount: int,
                                     user_id: str,
                                     user_email: Optional[str] = None) -> Dict:
        """Create payment for pay-per-use compute credits"""
        
        credit_price_usd = 0.10  # $0.10 per credit/hour
        total_price = credits_amount * credit_price_usd
        
        # Bulk purchase discounts
        if credits_amount >= 1000:
            discount = 0.20  # 20% discount for 1000+ credits
        elif credits_amount >= 500:
            discount = 0.15  # 15% discount for 500+ credits
        elif credits_amount >= 100:
            discount = 0.10  # 10% discount for 100+ credits
        else:
            discount = 0.0
        
        discounted_price = total_price * (1 - discount)
        
        charge_data = {
            "name": f"Mycelium Compute Credits - {credits_amount:,} credits",
            "description": f"Pay-per-use bio-algorithm computation credits",
            "local_price": {
                "amount": f"{discounted_price:.2f}",
                "currency": "USD"
            },
            "pricing_type": "fixed_price",
            "metadata": {
                "user_id": user_id,
                "type": "compute_credits",
                "credits_amount": str(credits_amount),
                "credit_price": str(credit_price_usd),
                "total_price": f"{total_price:.2f}",
                "bulk_discount": f"{discount:.2f}",
                "final_price": f"{discounted_price:.2f}"
            },
            "redirect_url": f"https://mycelium-ei-lang.com/credits/success",
            "cancel_url": f"https://mycelium-ei-lang.com/credits/cancel"
        }
        
        if user_email:
            charge_data["metadata"]["user_email"] = user_email
        
        try:
            response = requests.post(
                f"{self.base_url}/charges",
                headers=self.headers,
                json=charge_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Credits payment creation failed: {str(e)}"}
    
    def get_payment_status(self, charge_id: str) -> Dict:
        """Get payment status and details"""
        try:
            response = requests.get(
                f"{self.base_url}/charges/{charge_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json().get("data", {})
            
            # Determine payment status
            if data.get("confirmed_at"):
                status = PaymentStatus.CONFIRMED
            elif data.get("expired_at"):
                status = PaymentStatus.EXPIRED
            elif data.get("cancelled_at"):
                status = PaymentStatus.CANCELLED
            else:
                timeline = data.get("timeline", [])
                if any(event.get("status") == "FAILED" for event in timeline):
                    status = PaymentStatus.FAILED
                else:
                    status = PaymentStatus.PENDING
            
            return {
                "charge_id": charge_id,
                "status": status.value,
                "amount": data.get("pricing", {}).get("local", {}).get("amount"),
                "currency": data.get("pricing", {}).get("local", {}).get("currency"),
                "created_at": data.get("created_at"),
                "confirmed_at": data.get("confirmed_at"),
                "expires_at": data.get("expires_at"),
                "metadata": data.get("metadata", {}),
                "payments": data.get("payments", []),
                "hosted_url": data.get("hosted_url")
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Status check failed: {str(e)}"}
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Coinbase Commerce webhook signature"""
        if not self.webhook_secret:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_webhook(self, payload: bytes, signature: str) -> Dict:
        """Process Coinbase Commerce webhook"""
        if not self.verify_webhook_signature(payload, signature):
            return {"error": "Invalid webhook signature"}
        
        try:
            data = json.loads(payload.decode())
            event_type = data.get("event", {}).get("type")
            charge_data = data.get("event", {}).get("data", {})
            
            if event_type == "charge:confirmed":
                return self._handle_payment_confirmed(charge_data)
            elif event_type == "charge:failed":
                return self._handle_payment_failed(charge_data)
            elif event_type == "charge:delayed":
                return self._handle_payment_delayed(charge_data)
            else:
                return {"message": f"Unhandled event type: {event_type}"}
                
        except (json.JSONDecodeError, KeyError) as e:
            return {"error": f"Webhook processing failed: {str(e)}"}
    
    def _handle_payment_confirmed(self, charge_data: Dict) -> Dict:
        """Handle confirmed payment webhook"""
        metadata = charge_data.get("metadata", {})
        user_id = metadata.get("user_id")
        
        if metadata.get("type") == "compute_credits":
            # Handle compute credits purchase
            credits_amount = int(metadata.get("credits_amount", 0))
            return {
                "action": "add_compute_credits",
                "user_id": user_id,
                "credits": credits_amount,
                "charge_id": charge_data.get("id")
            }
        else:
            # Handle subscription payment
            plan = metadata.get("plan")
            duration = int(metadata.get("duration_months", 1))
            
            return {
                "action": "activate_subscription",
                "user_id": user_id,
                "plan": plan,
                "duration_months": duration,
                "charge_id": charge_data.get("id")
            }
    
    def _handle_payment_failed(self, charge_data: Dict) -> Dict:
        """Handle failed payment webhook"""
        metadata = charge_data.get("metadata", {})
        
        return {
            "action": "payment_failed",
            "user_id": metadata.get("user_id"),
            "charge_id": charge_data.get("id"),
            "reason": "Payment failed or was cancelled"
        }
    
    def _handle_payment_delayed(self, charge_data: Dict) -> Dict:
        """Handle delayed payment webhook"""
        metadata = charge_data.get("metadata", {})
        
        return {
            "action": "payment_delayed", 
            "user_id": metadata.get("user_id"),
            "charge_id": charge_data.get("id"),
            "message": "Payment is pending blockchain confirmation"
        }
    
    def get_pricing_tiers(self) -> Dict:
        """Get all pricing tiers with crypto discounts"""
        tiers = {}
        
        for plan, tier in self.PRICING_TIERS.items():
            crypto_price = tier.usd_price * (1 - tier.crypto_discount)
            savings = tier.usd_price - crypto_price
            
            tiers[plan.value] = {
                "name": tier.name,
                "usd_price": tier.usd_price,
                "crypto_price": crypto_price,
                "crypto_discount_percent": tier.crypto_discount * 100,
                "savings": savings,
                "features": tier.features,
                "api_calls": tier.api_calls,
                "support_level": tier.support_level
            }
        
        return tiers
    
    def get_supported_cryptocurrencies(self) -> Dict:
        """Get list of supported cryptocurrencies"""
        return self.SUPPORTED_CRYPTOCURRENCIES


# Usage example and testing
if __name__ == "__main__":
    # Initialize gateway (use environment variables for production)
    api_key = os.getenv("COINBASE_API_KEY", "test_key")
    webhook_secret = os.getenv("COINBASE_WEBHOOK_SECRET")
    
    gateway = MyceliumPaymentGateway(api_key, webhook_secret)
    
    # Example: Create professional subscription payment
    payment = gateway.create_subscription_payment(
        plan=SubscriptionPlan.PROFESSIONAL,
        user_id="user123",
        duration_months=12,
        user_email="user@example.com"
    )
    
    print("Payment created:")
    print(json.dumps(payment, indent=2))
    
    # Example: Create compute credits payment
    credits_payment = gateway.create_compute_credits_payment(
        credits_amount=500,
        user_id="user123",
        user_email="user@example.com"
    )
    
    print("\nCompute credits payment:")
    print(json.dumps(credits_payment, indent=2))
    
    # Example: Get pricing tiers
    pricing = gateway.get_pricing_tiers()
    print("\nPricing tiers:")
    print(json.dumps(pricing, indent=2))