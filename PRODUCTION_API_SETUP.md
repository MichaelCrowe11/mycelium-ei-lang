# 🔐 Production API Keys Configuration Guide

## 📋 Quick Setup Checklist

### 1️⃣ **Stripe Production Keys**

**Get your keys from**: https://dashboard.stripe.com/apikeys

```bash
# Production Keys Needed:
STRIPE_SECRET_KEY=sk_live_51...  # Your live secret key
STRIPE_PUBLISHABLE_KEY=pk_live_51...  # Your live publishable key
STRIPE_WEBHOOK_SECRET=whsec_...  # From webhook endpoint setup
```

**Setup Steps:**
1. Log into Stripe Dashboard
2. Switch to **LIVE MODE** (toggle in top-right)
3. Go to Developers → API keys
4. Copy your **Secret key** (starts with `sk_live_`)
5. Go to Developers → Webhooks
6. Add endpoint: `https://crypto-payments-8hr2wd0i5-michael-9927s-projects.vercel.app/webhooks/stripe`
7. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
8. Copy the **Signing secret** (starts with `whsec_`)

### 2️⃣ **Coinbase Commerce Production Keys**

**Get your keys from**: https://commerce.coinbase.com/settings/security

```bash
# Production Keys Needed:
COINBASE_API_KEY=your_api_key_here
COINBASE_WEBHOOK_SECRET=your_webhook_shared_secret
```

**Setup Steps:**
1. Log into Coinbase Commerce
2. Go to Settings → API keys
3. Create new API key or use existing
4. Copy the API key
5. Go to Settings → Webhook subscriptions
6. Add endpoint: `https://crypto-payments-8hr2wd0i5-michael-9927s-projects.vercel.app/webhooks/coinbase`
7. Copy the **Shared secret**

### 3️⃣ **Add Keys to Vercel**

**Via Vercel Dashboard:**
1. Go to: https://vercel.com/dashboard
2. Select project: `crypto-payments`
3. Go to Settings → Environment Variables
4. Add each key:
   - Name: `STRIPE_SECRET_KEY`
   - Value: `sk_live_...`
   - Environment: Production ✓
   - Click "Save"
5. Repeat for all keys

**Via CLI (Alternative):**
```bash
cd mycelium-ei-lang/crypto-payments

# Add Stripe keys
vercel env add STRIPE_SECRET_KEY production
vercel env add STRIPE_PUBLISHABLE_KEY production
vercel env add STRIPE_WEBHOOK_SECRET production

# Add Coinbase keys
vercel env add COINBASE_API_KEY production
vercel env add COINBASE_WEBHOOK_SECRET production

# Redeploy with new environment variables
vercel --prod
```

### 4️⃣ **Create Stripe Products & Prices**

Run this script once to create products in Stripe:

```python
# create_stripe_products.py
import stripe
import os

stripe.api_key = "sk_live_YOUR_KEY_HERE"

# Create Professional Plan
professional = stripe.Product.create(
    name="Mycelium-EI Professional",
    description="Commercial bio-algorithms, Priority support, GPU acceleration"
)

stripe.Price.create(
    product=professional.id,
    unit_amount=29900,  # $299.00
    currency="usd",
    recurring={"interval": "month"},
    lookup_key="professional_monthly"
)

stripe.Price.create(
    product=professional.id,
    unit_amount=299900,  # $2,999.00
    currency="usd",
    recurring={"interval": "year"},
    lookup_key="professional_yearly"
)

# Create Enterprise Plan
enterprise = stripe.Product.create(
    name="Mycelium-EI Enterprise",
    description="Unlimited algorithms, Dedicated support, Custom integrations"
)

stripe.Price.create(
    product=enterprise.id,
    unit_amount=299900,  # $2,999.00
    currency="usd",
    recurring={"interval": "month"},
    lookup_key="enterprise_monthly"
)

stripe.Price.create(
    product=enterprise.id,
    unit_amount=2999900,  # $29,999.00
    currency="usd",
    recurring={"interval": "year"},
    lookup_key="enterprise_yearly"
)

# Create Quantum Plan
quantum = stripe.Product.create(
    name="Mycelium-EI Quantum",
    description="Quantum computing, White-label licensing, Research partnerships"
)

stripe.Price.create(
    product=quantum.id,
    unit_amount=999900,  # $9,999.00
    currency="usd",
    recurring={"interval": "month"},
    lookup_key="quantum_monthly"
)

stripe.Price.create(
    product=quantum.id,
    unit_amount=9999900,  # $99,999.00
    currency="usd",
    recurring={"interval": "year"},
    lookup_key="quantum_yearly"
)

print("✅ Products and prices created successfully!")
```

### 5️⃣ **Test Production Payments**

**Test with small amount first:**
1. Visit: https://crypto-payments-8hr2wd0i5-michael-9927s-projects.vercel.app
2. Select Professional plan
3. Choose monthly billing
4. Test with credit card (Stripe)
5. Test with crypto (small USDC amount)
6. Verify webhook delivery in dashboards

### 6️⃣ **OAuth & Additional Security**

```bash
# Already configured from earlier:
OAUTH_CLIENT_ID=5bc1d0f3-894f-4d02-988e-b36076530b1c
OAUTH_CLIENT_SECRET=pUd5Z0yx9dJo4o6NIn4Ox4Idvv

# Add these for extra security:
JWT_SECRET_KEY=$(openssl rand -hex 32)
API_SECRET_KEY=$(openssl rand -hex 32)
```

## ⚠️ **Important Security Notes**

1. **NEVER commit API keys to GitHub**
2. **Use environment variables only**
3. **Rotate keys every 90 days**
4. **Monitor webhook logs for failures**
5. **Set up alerts for payment failures**
6. **Enable 2FA on Stripe and Coinbase accounts**

## 🧪 **Verification Checklist**

- [ ] Stripe live mode activated
- [ ] Coinbase Commerce account verified
- [ ] All environment variables added to Vercel
- [ ] Webhook endpoints configured
- [ ] Products created in Stripe
- [ ] Test transaction completed
- [ ] Webhook received successfully
- [ ] Email notifications working

## 📞 **Support Contacts**

- **Stripe Support**: https://support.stripe.com
- **Coinbase Commerce**: https://commerce.coinbase.com/help
- **Vercel Support**: https://vercel.com/support

---

Once configured, your payment system will be **FULLY OPERATIONAL** and ready to process real customer payments! 💰🚀