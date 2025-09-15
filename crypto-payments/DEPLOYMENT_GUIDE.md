# 🚀 Production Deployment Guide - Mycelium Payment Gateway

## Quick Deploy Options

### 🎯 Option 1: Railway (Recommended - Fastest)

**1-Click Deploy:**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/mycelium-payments)

**Manual Deploy:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway add --service postgresql
railway add --service redis
railway deploy
```

**Set Environment Variables:**
```bash
railway variables set COINBASE_API_KEY="your_api_key_here"
railway variables set COINBASE_WEBHOOK_SECRET="your_webhook_secret_here"
```

**Expected URL:** `https://mycelium-payments-production.up.railway.app`

---

### 🎯 Option 2: Render

**1-Click Deploy:**
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/MichaelCrowe11/pulsar-lang)

**Manual Deploy:**
1. Fork the repository
2. Connect to Render
3. Create new Web Service from `/crypto-payments/`
4. Auto-deploy enabled from `render.yaml`

**Set Environment Variables in Render Dashboard:**
- `COINBASE_API_KEY` = `your_api_key_here`
- `COINBASE_WEBHOOK_SECRET` = `your_webhook_secret_here`

---

### 🎯 Option 3: Heroku

**1-Click Deploy:**
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/MichaelCrowe11/pulsar-lang)

**Manual Deploy:**
```bash
# Install Heroku CLI
npm install -g heroku

# Deploy
heroku create mycelium-payment-gateway
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
git subtree push --prefix=crypto-payments heroku main
```

---

### 🎯 Option 4: Vercel (Serverless)

**1-Click Deploy:**
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FMichaelCrowe11%2Fpulsar-lang&project-name=mycelium-payments&repository-name=mycelium-payments)

**Manual Deploy:**
```bash
# Install Vercel CLI
npm install -g vercel

cd crypto-payments
vercel --prod
```

**Set Environment Variables:**
```bash
vercel env add COINBASE_API_KEY
vercel env add COINBASE_WEBHOOK_SECRET
```

---

### 🎯 Option 5: DigitalOcean App Platform

**1-Click Deploy:**
[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/MichaelCrowe11/pulsar-lang/tree/main/crypto-payments)

**Manual Deploy:**
1. Create new App in DigitalOcean
2. Connect GitHub repository
3. Set source directory: `/crypto-payments`
4. Add PostgreSQL and Redis databases
5. Configure environment variables

---

## 🔧 Production Configuration

### Required Environment Variables
```bash
# Coinbase Commerce API
COINBASE_API_KEY="ddae9bb3-3f56-435b-94fa-5df58d670f45"
COINBASE_WEBHOOK_SECRET="your_webhook_secret"

# Database (auto-configured by most platforms)
DATABASE_URL="postgresql://user:pass@host:5432/dbname"
REDIS_URL="redis://user:pass@host:6379"

# Security
JWT_SECRET_KEY="auto-generated-secret"
API_SECRET_KEY="auto-generated-secret"

# Optional
EMAIL_API_KEY="your_sendgrid_key"
SENTRY_DSN="your_sentry_dsn"
```

### Performance Settings
```bash
# Server
PORT=8000
WORKERS=4
MAX_REQUESTS=1000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=INFO
```

## 🔒 Security Checklist

### Before Production Launch:
- [ ] Set strong `JWT_SECRET_KEY` and `API_SECRET_KEY`
- [ ] Enable HTTPS/SSL certificates (auto on most platforms)
- [ ] Configure CORS origins for your domain
- [ ] Set up webhook endpoint verification
- [ ] Enable rate limiting
- [ ] Configure logging and monitoring

### Domain Configuration:
```bash
# Custom domain setup (varies by platform)
# Railway: railway domain add yourdomain.com
# Render: Add custom domain in dashboard
# Heroku: heroku domains:add yourdomain.com
# Vercel: vercel domains add yourdomain.com
```

## 📊 Monitoring & Analytics

### Health Checks
All platforms automatically monitor:
- `GET /health` - API health status
- Database connectivity
- Redis cache availability
- Payment gateway status

### Logging
Production logs include:
- Payment processing events
- Webhook deliveries
- Error tracking
- Performance metrics

### Recommended Monitoring:
- **Sentry** for error tracking
- **LogRocket** for user sessions
- **Datadog** for infrastructure monitoring

## 🧪 Testing Production Deployment

### 1. Health Check
```bash
curl https://your-app-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-12T08:41:15.912Z",
  "services": {
    "payment_gateway": true,
    "tokenomics": true
  }
}
```

### 2. API Documentation
Visit: `https://your-app-url.com/docs`

### 3. Payment Portal
Visit: `https://your-app-url.com/`

### 4. Test Payment Flow
1. Select subscription tier
2. Choose cryptocurrency
3. Complete payment (use testnet/small amounts)
4. Verify webhook processing

## 🚀 Go-Live Checklist

### Pre-Launch (24 hours before):
- [ ] Deploy to production platform
- [ ] Configure custom domain
- [ ] Test all payment flows
- [ ] Set up monitoring
- [ ] Configure backup systems

### Launch Day:
- [ ] Monitor system performance
- [ ] Check webhook deliveries
- [ ] Verify payment processing
- [ ] Monitor error rates
- [ ] Update documentation

### Post-Launch (48 hours):
- [ ] Analyze performance metrics
- [ ] Review error logs
- [ ] Gather user feedback
- [ ] Plan optimization improvements

## 💡 Platform Recommendations

### For MVP/Testing: **Railway** 
- Fastest deployment
- Automatic scaling
- Built-in databases
- Great developer experience

### For High Traffic: **Render**
- Better performance at scale
- Advanced monitoring
- Multiple regions
- Professional support

### For Enterprise: **DigitalOcean**
- Full infrastructure control
- Custom configurations
- Dedicated resources
- Enterprise SLA

## 📞 Support & Troubleshooting

### Common Issues:
1. **Environment variables not set**: Check platform dashboard
2. **Database connection failed**: Verify DATABASE_URL format
3. **Webhook verification failed**: Check COINBASE_WEBHOOK_SECRET
4. **CORS errors**: Update allowed origins in settings

### Support Channels:
- GitHub Issues: https://github.com/MichaelCrowe11/pulsar-lang/issues
- Documentation: https://michaelcrowe11.github.io/pulsar-lang/
- Discord: [Join Server](https://discord.gg/mycelium-ei-lang)

---

🎉 **Your payment gateway is ready for production!** Choose your preferred platform and deploy in under 10 minutes.