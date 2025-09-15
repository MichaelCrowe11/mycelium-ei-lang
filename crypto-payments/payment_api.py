"""
Payment Gateway API Server for Mycelium-EI-Lang
FastAPI backend integrating Coinbase Commerce and MYC token economics
"""

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
import os
import json
import logging
from datetime import datetime, timedelta

from coinbase_gateway import MyceliumPaymentGateway, SubscriptionPlan, PaymentStatus
from tokenomics import MyceliumTokenomics, StakingTier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mycelium Payment Gateway API",
    description="Cryptocurrency payment processing for Mycelium-EI-Lang platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="crypto-payments"), name="static")

# Initialize payment gateway and tokenomics
try:
    coinbase_api_key = os.getenv("COINBASE_API_KEY")
    coinbase_webhook_secret = os.getenv("COINBASE_WEBHOOK_SECRET")
    
    if not coinbase_api_key:
        logger.warning("COINBASE_API_KEY not found in environment variables")
        coinbase_api_key = "demo_key"  # For development
    
    payment_gateway = MyceliumPaymentGateway(coinbase_api_key, coinbase_webhook_secret)
    tokenomics = MyceliumTokenomics()
    
except Exception as e:
    logger.error(f"Failed to initialize payment systems: {e}")
    payment_gateway = None
    tokenomics = MyceliumTokenomics()

# Pydantic models
class SubscriptionRequest(BaseModel):
    plan: str
    user_id: str
    duration_months: int = 1
    user_email: Optional[EmailStr] = None

class ComputeCreditsRequest(BaseModel):
    credits_amount: int
    user_id: str
    user_email: Optional[EmailStr] = None

class StakingCalculationRequest(BaseModel):
    stake_amount: int
    days_staked: int

class PaymentStatusResponse(BaseModel):
    status: str
    charge_id: str
    amount: Optional[str] = None
    currency: Optional[str] = None
    created_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    expires_at: Optional[str] = None
    hosted_url: Optional[str] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def payment_portal():
    """Serve the main payment portal"""
    return FileResponse("crypto-payments/payment_frontend.html")

@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "payment_gateway": payment_gateway is not None,
            "tokenomics": tokenomics is not None
        }
    }

@app.get("/pricing")
async def get_pricing_tiers():
    """Get all subscription pricing tiers with crypto discounts"""
    if not payment_gateway:
        raise HTTPException(status_code=503, detail="Payment gateway not available")
    
    pricing = payment_gateway.get_pricing_tiers()
    supported_crypto = payment_gateway.get_supported_cryptocurrencies()
    
    return {
        "pricing_tiers": pricing,
        "supported_cryptocurrencies": supported_crypto,
        "crypto_benefits": {
            "discounts": "Save 10-20% on all plans",
            "instant_processing": "Payments confirmed in minutes",
            "global_access": "Pay from anywhere in the world",
            "privacy": "Pseudonymous transactions"
        }
    }

@app.post("/payments/subscription")
async def create_subscription_payment(request: SubscriptionRequest):
    """Create a cryptocurrency payment for subscription"""
    if not payment_gateway:
        raise HTTPException(status_code=503, detail="Payment gateway not available")
    
    try:
        # Validate subscription plan
        plan = SubscriptionPlan(request.plan.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {request.plan}")
    
    if request.duration_months < 1 or request.duration_months > 36:
        raise HTTPException(status_code=400, detail="Duration must be between 1 and 36 months")
    
    try:
        result = payment_gateway.create_subscription_payment(
            plan=plan,
            user_id=request.user_id,
            duration_months=request.duration_months,
            user_email=request.user_email
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Subscription payment creation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment creation failed")

@app.post("/payments/credits")
async def create_credits_payment(request: ComputeCreditsRequest):
    """Create a payment for compute credits"""
    if not payment_gateway:
        raise HTTPException(status_code=503, detail="Payment gateway not available")
    
    if request.credits_amount < 1 or request.credits_amount > 100000:
        raise HTTPException(status_code=400, detail="Credits amount must be between 1 and 100,000")
    
    try:
        result = payment_gateway.create_compute_credits_payment(
            credits_amount=request.credits_amount,
            user_id=request.user_id,
            user_email=request.user_email
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Credits payment creation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment creation failed")

@app.get("/payments/{charge_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(charge_id: str):
    """Get payment status and details"""
    if not payment_gateway:
        raise HTTPException(status_code=503, detail="Payment gateway not available")
    
    try:
        result = payment_gateway.get_payment_status(charge_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return PaymentStatusResponse(**result)
        
    except Exception as e:
        logger.error(f"Payment status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@app.post("/webhooks/coinbase")
async def coinbase_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Coinbase Commerce webhooks"""
    if not payment_gateway:
        raise HTTPException(status_code=503, detail="Payment gateway not available")
    
    try:
        payload = await request.body()
        signature = request.headers.get("X-CC-Webhook-Signature", "")
        
        result = payment_gateway.process_webhook(payload, signature)
        
        if "error" in result:
            logger.error(f"Webhook processing error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Process the webhook result in background
        background_tasks.add_task(process_payment_confirmation, result)
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def process_payment_confirmation(webhook_result: Dict):
    """Background task to process confirmed payments"""
    try:
        action = webhook_result.get("action")
        
        if action == "activate_subscription":
            # Handle subscription activation
            user_id = webhook_result.get("user_id")
            plan = webhook_result.get("plan")
            duration = webhook_result.get("duration_months")
            
            logger.info(f"Activating {plan} subscription for user {user_id} for {duration} months")
            # TODO: Integrate with user management system
            
        elif action == "add_compute_credits":
            # Handle compute credits addition
            user_id = webhook_result.get("user_id")
            credits = webhook_result.get("credits")
            
            logger.info(f"Adding {credits} compute credits to user {user_id}")
            # TODO: Integrate with credit system
            
        elif action == "payment_failed":
            # Handle payment failure
            user_id = webhook_result.get("user_id")
            reason = webhook_result.get("reason")
            
            logger.warning(f"Payment failed for user {user_id}: {reason}")
            # TODO: Send notification to user
            
    except Exception as e:
        logger.error(f"Payment confirmation processing failed: {e}")

# Token economics endpoints
@app.get("/tokenomics/allocation")
async def get_token_allocation():
    """Get MYC token allocation breakdown"""
    return tokenomics.get_token_allocation_summary()

@app.post("/tokenomics/staking/calculate")
async def calculate_staking_rewards(request: StakingCalculationRequest):
    """Calculate staking rewards and benefits"""
    if request.stake_amount < 0 or request.days_staked < 0:
        raise HTTPException(status_code=400, detail="Amounts must be non-negative")
    
    rewards = tokenomics.calculate_staking_rewards(request.stake_amount, request.days_staked)
    governance = tokenomics.calculate_governance_power(request.stake_amount)
    
    return {
        "staking_rewards": rewards,
        "governance_power": governance
    }

@app.get("/tokenomics/price-projection")
async def get_price_projection(months: int = 36):
    """Get MYC token price projections"""
    if months < 1 or months > 120:
        raise HTTPException(status_code=400, detail="Months must be between 1 and 120")
    
    return tokenomics.get_token_price_projection(months)

@app.get("/tokenomics/utility")
async def get_token_utility():
    """Get token utility and economic model"""
    return tokenomics.get_utility_economics()

@app.get("/tokenomics/smart-contract")
async def get_smart_contract_spec():
    """Get Solidity smart contract specification"""
    return {
        "contract_name": "MyceliumToken",
        "symbol": "MYC",
        "total_supply": "1,000,000,000",
        "features": [
            "ERC-20 compliant",
            "Staking rewards",
            "Governance voting", 
            "Deflationary burn mechanics",
            "Multi-tier system"
        ],
        "solidity_code": tokenomics.generate_smart_contract_spec()
    }

# Statistics and analytics
@app.get("/analytics/payment-stats")
async def get_payment_statistics():
    """Get payment processing statistics"""
    # TODO: Implement payment statistics from database
    return {
        "total_payments": 0,
        "total_volume_usd": 0,
        "active_subscriptions": 0,
        "popular_plans": [],
        "cryptocurrency_breakdown": {},
        "monthly_recurring_revenue": 0
    }

@app.get("/analytics/token-metrics")
async def get_token_metrics():
    """Get MYC token metrics and statistics"""
    # TODO: Implement real token metrics from blockchain
    return {
        "total_supply": tokenomics.TOTAL_SUPPLY,
        "circulating_supply": 200_000_000,  # Example
        "total_staked": 50_000_000,  # Example
        "staking_participation_rate": 25.0,  # Example
        "average_staking_duration_days": 180,  # Example
        "governance_proposals_active": 3,  # Example
        "burn_rate_monthly": 100_000  # Example
    }

# Admin endpoints (should be protected in production)
@app.get("/admin/config")
async def get_admin_config():
    """Get payment gateway configuration (admin only)"""
    return {
        "coinbase_configured": bool(os.getenv("COINBASE_API_KEY")),
        "webhook_configured": bool(os.getenv("COINBASE_WEBHOOK_SECRET")),
        "supported_cryptocurrencies": list(payment_gateway.SUPPORTED_CRYPTOCURRENCIES.keys()) if payment_gateway else [],
        "pricing_tiers": len(payment_gateway.PRICING_TIERS) if payment_gateway else 0,
        "staking_tiers": len(tokenomics.STAKING_TIERS)
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "payment_api:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )