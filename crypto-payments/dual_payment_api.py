"""
Dual Payment Gateway API - Both Stripe and Crypto Support
FastAPI backend supporting both traditional credit cards and cryptocurrency
"""

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
import os
import json
import logging
from datetime import datetime

from coinbase_gateway import MyceliumPaymentGateway, SubscriptionPlan
from stripe_gateway import MyceliumStripeGateway
from tokenomics import MyceliumTokenomics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mycelium Dual Payment Gateway",
    description="Credit card and cryptocurrency payments for Mycelium-EI-Lang platform", 
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize payment gateways
try:
    # Coinbase for crypto payments
    coinbase_api_key = os.getenv("COINBASE_API_KEY", "demo_key")
    coinbase_webhook_secret = os.getenv("COINBASE_WEBHOOK_SECRET")
    crypto_gateway = MyceliumPaymentGateway(coinbase_api_key, coinbase_webhook_secret)
    
    # Stripe for credit card payments
    stripe_api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_demo")
    stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    stripe_gateway = MyceliumStripeGateway(stripe_api_key, stripe_webhook_secret)
    
    # Tokenomics
    tokenomics = MyceliumTokenomics()
    
    logger.info("Payment gateways initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize payment systems: {e}")
    crypto_gateway = None
    stripe_gateway = None
    tokenomics = MyceliumTokenomics()

# Pydantic models
class SubscriptionRequest(BaseModel):
    plan: str
    payment_method: str  # "crypto" or "stripe"
    user_email: EmailStr
    billing_cycle: str = "monthly"  # "monthly" or "yearly"
    duration_months: int = 1  # For crypto payments

class ComputeCreditsRequest(BaseModel):
    credits_amount: int
    payment_method: str  # "crypto" or "stripe" 
    user_email: EmailStr

class PaymentMethodComparison(BaseModel):
    plan: str
    crypto_price: float
    stripe_price: float
    crypto_discount: float
    stripe_discount: float
    savings_with_crypto: float
    recommended: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def dual_payment_portal():
    """Serve dual payment portal with both options"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mycelium Payment Portal - Crypto & Credit Cards</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                max-width: 1200px; margin: 0 auto; padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333; min-height: 100vh;
            }
            .container { background: white; border-radius: 16px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
            h1 { text-align: center; color: #2d3748; margin-bottom: 40px; font-size: 2.5rem; }
            .payment-methods { display: flex; gap: 20px; margin-bottom: 40px; }
            .method-card { 
                flex: 1; padding: 20px; border: 2px solid #e2e8f0; border-radius: 12px; 
                cursor: pointer; transition: all 0.3s ease; text-align: center;
            }
            .method-card:hover, .method-card.selected { border-color: #667eea; background: #f7fafc; }
            .method-icon { font-size: 2rem; margin-bottom: 10px; }
            .pricing-tiers { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .tier { 
                border: 1px solid #e2e8f0; padding: 30px; border-radius: 12px; 
                position: relative; background: #fafafa; transition: transform 0.3s ease;
            }
            .tier:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
            .tier.popular { border-color: #667eea; background: linear-gradient(135deg, #667eea10, #764ba210); }
            .tier.popular::before { 
                content: 'MOST POPULAR'; position: absolute; top: -10px; left: 50%; 
                transform: translateX(-50%); background: #667eea; color: white; 
                padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;
            }
            .tier-name { font-size: 1.5rem; font-weight: 600; margin-bottom: 10px; }
            .tier-price { font-size: 2rem; font-weight: bold; color: #2d5aa0; margin-bottom: 10px; }
            .tier-discount { color: #48bb78; font-weight: 600; margin-bottom: 20px; }
            .tier-features { list-style: none; padding: 0; margin-bottom: 30px; }
            .tier-features li { padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
            .tier-features li:before { content: '✓'; color: #48bb78; font-weight: bold; margin-right: 10px; }
            button { 
                width: 100%; background: linear-gradient(135deg, #667eea, #764ba2); 
                color: white; padding: 12px 20px; border: none; border-radius: 8px; 
                cursor: pointer; font-size: 1rem; font-weight: 600; transition: transform 0.2s;
            }
            button:hover { transform: scale(1.05); }
            .free-button { background: #48bb78; }
            .comparison { margin-top: 40px; padding: 20px; background: #f7fafc; border-radius: 12px; }
            .toggle-billing { text-align: center; margin-bottom: 30px; }
            .toggle { 
                display: inline-flex; background: #e2e8f0; border-radius: 25px; 
                padding: 3px; position: relative;
            }
            .toggle input { display: none; }
            .toggle label { 
                padding: 10px 20px; cursor: pointer; border-radius: 25px; 
                transition: background 0.3s ease; position: relative; z-index: 1;
            }
            .toggle input:checked + label { background: #667eea; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧬 Mycelium-EI-Lang Payment Portal</h1>
            <p style="text-align: center; font-size: 1.1rem; color: #666; margin-bottom: 40px;">
                Choose your preferred payment method for bio-inspired programming platform access
            </p>
            
            <div class="payment-methods">
                <div class="method-card" id="crypto-method" onclick="selectMethod('crypto')">
                    <div class="method-icon">₿</div>
                    <h3>Cryptocurrency</h3>
                    <p>Bitcoin, Ethereum, USDC & more</p>
                    <p><strong>Save up to 20%</strong></p>
                </div>
                <div class="method-card selected" id="stripe-method" onclick="selectMethod('stripe')">
                    <div class="method-icon">💳</div>
                    <h3>Credit Card</h3>
                    <p>Visa, Mastercard, American Express</p>
                    <p><strong>Instant activation</strong></p>
                </div>
            </div>
            
            <div class="toggle-billing">
                <div class="toggle">
                    <input type="radio" id="monthly" name="billing" value="monthly" checked>
                    <label for="monthly">Monthly</label>
                    <input type="radio" id="yearly" name="billing" value="yearly">
                    <label for="yearly">Yearly (2 months free!)</label>
                </div>
            </div>
            
            <div class="pricing-tiers">
                <div class="tier">
                    <div class="tier-name">Community</div>
                    <div class="tier-price">FREE</div>
                    <div class="tier-discount">Always free forever</div>
                    <ul class="tier-features">
                        <li>Basic bio-algorithms</li>
                        <li>Community support</li>
                        <li>1,000 API calls/month</li>
                    </ul>
                    <button class="free-button" onclick="selectPlan('community')">Get Started Free</button>
                </div>
                
                <div class="tier popular">
                    <div class="tier-name">Professional</div>
                    <div class="tier-price" id="professional-price">$299/month</div>
                    <div class="tier-discount" id="professional-discount">Save $30 with crypto payments</div>
                    <ul class="tier-features">
                        <li>Commercial bio-algorithms</li>
                        <li>Priority support</li>
                        <li>GPU acceleration</li>
                        <li>100,000 API calls/month</li>
                    </ul>
                    <button onclick="selectPlan('professional')">Choose Professional</button>
                </div>
                
                <div class="tier">
                    <div class="tier-name">Enterprise</div>
                    <div class="tier-price" id="enterprise-price">$2,999/month</div>
                    <div class="tier-discount" id="enterprise-discount">Save $450 with crypto payments</div>
                    <ul class="tier-features">
                        <li>Unlimited algorithms</li>
                        <li>Dedicated support</li>
                        <li>Custom integrations</li>
                        <li>10M API calls/month</li>
                    </ul>
                    <button onclick="selectPlan('enterprise')">Choose Enterprise</button>
                </div>
                
                <div class="tier">
                    <div class="tier-name">Quantum</div>
                    <div class="tier-price" id="quantum-price">$9,999/month</div>
                    <div class="tier-discount" id="quantum-discount">Save $2,000 with crypto payments</div>
                    <ul class="tier-features">
                        <li>Quantum computing access</li>
                        <li>White-label licensing</li>
                        <li>Research partnerships</li>
                        <li>Unlimited API calls</li>
                    </ul>
                    <button onclick="selectPlan('quantum')">Choose Quantum</button>
                </div>
            </div>
            
            <div class="comparison">
                <h3>💡 Why choose cryptocurrency payments?</h3>
                <ul style="columns: 2; column-gap: 40px;">
                    <li><strong>Significant Savings:</strong> 10-20% discount on all plans</li>
                    <li><strong>Global Access:</strong> Pay from anywhere in the world</li>
                    <li><strong>Privacy:</strong> Pseudonymous transactions</li>
                    <li><strong>Fast Settlement:</strong> Payments confirmed in minutes</li>
                    <li><strong>No Chargebacks:</strong> Final settlement protection</li>
                    <li><strong>Lower Fees:</strong> Avoid credit card processing costs</li>
                </ul>
            </div>
        </div>
        
        <script>
            let selectedMethod = 'stripe';
            let selectedBilling = 'monthly';
            
            const pricing = {
                monthly: {
                    professional: { stripe: 299, crypto: 269 },
                    enterprise: { stripe: 2999, crypto: 2549 },
                    quantum: { stripe: 9999, crypto: 7999 }
                },
                yearly: {
                    professional: { stripe: 2999, crypto: 2549 },
                    enterprise: { stripe: 29999, crypto: 25499 },
                    quantum: { stripe: 99999, crypto: 79999 }
                }
            };
            
            function selectMethod(method) {
                selectedMethod = method;
                document.querySelectorAll('.method-card').forEach(card => card.classList.remove('selected'));
                document.getElementById(method + '-method').classList.add('selected');
                updatePricing();
            }
            
            function updatePricing() {
                const billingCycle = document.querySelector('input[name="billing"]:checked').value;
                selectedBilling = billingCycle;
                
                ['professional', 'enterprise', 'quantum'].forEach(plan => {
                    const price = pricing[billingCycle][plan][selectedMethod];
                    const savings = pricing[billingCycle][plan].stripe - pricing[billingCycle][plan].crypto;
                    
                    document.getElementById(plan + '-price').textContent = 
                        billingCycle === 'yearly' ? `$${price.toLocaleString()}/year` : `$${price.toLocaleString()}/month`;
                    
                    if (selectedMethod === 'crypto') {
                        document.getElementById(plan + '-discount').textContent = `Save $${savings.toLocaleString()} with crypto payments`;
                        document.getElementById(plan + '-discount').style.display = 'block';
                    } else {
                        document.getElementById(plan + '-discount').textContent = billingCycle === 'yearly' ? '2 months free with yearly billing' : 'Instant activation';
                        document.getElementById(plan + '-discount').style.display = 'block';
                    }
                });
            }
            
            document.querySelectorAll('input[name="billing"]').forEach(radio => {
                radio.addEventListener('change', updatePricing);
            });
            
            function selectPlan(plan) {
                if (plan === 'community') {
                    alert('Community plan activated! No payment required. Check your email for access instructions.');
                    return;
                }
                
                const email = prompt('Enter your email address:');
                if (!email) return;
                
                const requestData = {
                    plan: plan,
                    payment_method: selectedMethod,
                    user_email: email,
                    billing_cycle: selectedBilling
                };
                
                fetch('/create-subscription-checkout', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(requestData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.checkout_url) {
                        window.open(data.checkout_url, '_blank');
                    } else if (data.data && data.data.hosted_url) {
                        window.open(data.data.hosted_url, '_blank');
                    } else {
                        alert('Payment setup: ' + JSON.stringify(data));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error creating payment. Please try again.');
                });
            }
            
            // Initialize pricing
            updatePricing();
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_template)

@app.get("/health")
async def health_check():
    """API health check for both payment methods"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "payment_methods": {
            "cryptocurrency": crypto_gateway is not None,
            "credit_card": stripe_gateway is not None,
            "tokenomics": tokenomics is not None
        },
        "demo_mode": {
            "crypto": crypto_gateway and crypto_gateway.api_key == "demo_key",
            "stripe": stripe_gateway and "test" in stripe_gateway.api_key
        }
    }

@app.get("/pricing/compare")
async def compare_pricing():
    """Compare pricing between crypto and credit card payments"""
    comparisons = []
    
    crypto_pricing = crypto_gateway.get_pricing_tiers() if crypto_gateway else {}
    stripe_pricing = stripe_gateway.get_pricing_summary() if stripe_gateway else {}
    
    for plan in ["professional", "enterprise", "quantum"]:
        if plan in crypto_pricing and plan in stripe_pricing:
            crypto_monthly = crypto_pricing[plan]["crypto_price"]
            stripe_monthly = stripe_pricing[plan]["monthly_price"]
            
            comparison = PaymentMethodComparison(
                plan=plan,
                crypto_price=crypto_monthly,
                stripe_price=stripe_monthly,
                crypto_discount=crypto_pricing[plan]["crypto_discount_percent"],
                stripe_discount=stripe_pricing[plan]["stripe_discount"],
                savings_with_crypto=stripe_monthly - crypto_monthly,
                recommended="crypto" if crypto_monthly < stripe_monthly else "stripe"
            )
            comparisons.append(comparison)
    
    return {
        "comparisons": comparisons,
        "overall_recommendation": "crypto",
        "crypto_benefits": [
            "10-20% discount on all paid plans",
            "Global accessibility",
            "Faster settlement",
            "Lower processing fees",
            "Enhanced privacy"
        ]
    }

@app.post("/create-subscription-checkout")
async def create_subscription_checkout(request: SubscriptionRequest):
    """Create checkout session for either Stripe or crypto"""
    
    if request.payment_method == "crypto":
        if not crypto_gateway:
            raise HTTPException(status_code=503, detail="Cryptocurrency payments not available")
        
        try:
            plan = SubscriptionPlan(request.plan.lower())
            result = crypto_gateway.create_subscription_payment(
                plan=plan,
                user_id=request.user_email,
                duration_months=request.duration_months,
                user_email=request.user_email
            )
            
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return result
            
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {request.plan}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Crypto payment failed: {str(e)}")
    
    elif request.payment_method == "stripe":
        if not stripe_gateway:
            raise HTTPException(status_code=503, detail="Credit card payments not available")
        
        try:
            result = stripe_gateway.create_subscription_checkout(
                plan=request.plan.lower(),
                customer_email=request.user_email,
                billing_cycle=request.billing_cycle,
                success_url="https://mycelium-ei-lang.com/success",
                cancel_url="https://mycelium-ei-lang.com/cancel"
            )
            
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Credit card payment failed: {str(e)}")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method. Use 'crypto' or 'stripe'")

@app.post("/create-credits-checkout")
async def create_credits_checkout(request: ComputeCreditsRequest):
    """Create checkout for compute credits with either payment method"""
    
    if request.payment_method == "crypto":
        if not crypto_gateway:
            raise HTTPException(status_code=503, detail="Cryptocurrency payments not available")
        
        result = crypto_gateway.create_compute_credits_payment(
            credits_amount=request.credits_amount,
            user_id=request.user_email,
            user_email=request.user_email
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    elif request.payment_method == "stripe":
        if not stripe_gateway:
            raise HTTPException(status_code=503, detail="Credit card payments not available")
        
        result = stripe_gateway.create_credits_checkout(
            credits_amount=request.credits_amount,
            customer_email=request.user_email,
            success_url="https://mycelium-ei-lang.com/credits/success",
            cancel_url="https://mycelium-ei-lang.com/credits/cancel"
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Stripe webhook events"""
    if not stripe_gateway:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature", "")
        
        result = stripe_gateway.process_webhook(payload, signature)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Process webhook result in background
        background_tasks.add_task(process_stripe_webhook, result)
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Stripe webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@app.post("/webhooks/coinbase")
async def coinbase_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Coinbase Commerce webhook events"""
    if not crypto_gateway:
        raise HTTPException(status_code=503, detail="Coinbase not configured")
    
    try:
        payload = await request.body()
        signature = request.headers.get("X-CC-Webhook-Signature", "")
        
        result = crypto_gateway.process_webhook(payload, signature)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Process webhook result in background
        background_tasks.add_task(process_crypto_webhook, result)
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Coinbase webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def process_stripe_webhook(webhook_result: Dict):
    """Process Stripe webhook events"""
    action = webhook_result.get("action")
    logger.info(f"Processing Stripe webhook: {action}")
    
    # TODO: Integrate with user management system
    if action == "activate_subscription":
        logger.info(f"Activating subscription for {webhook_result.get('customer_email')}")
    elif action == "add_compute_credits":
        logger.info(f"Adding credits for {webhook_result.get('customer_email')}")

async def process_crypto_webhook(webhook_result: Dict):
    """Process crypto webhook events"""
    action = webhook_result.get("action")
    logger.info(f"Processing crypto webhook: {action}")
    
    # TODO: Integrate with user management system
    if action == "activate_subscription":
        logger.info(f"Activating crypto subscription for {webhook_result.get('user_id')}")
    elif action == "add_compute_credits":
        logger.info(f"Adding crypto credits for {webhook_result.get('user_id')}")

@app.get("/tokenomics")
async def get_tokenomics():
    """Get MYC token economics information"""
    return {
        "allocation": tokenomics.get_token_allocation_summary(),
        "staking_tiers": tokenomics.STAKING_TIERS,
        "utility": tokenomics.get_utility_economics()
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "dual_payment_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )