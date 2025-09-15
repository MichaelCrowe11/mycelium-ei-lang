"""
Simplified Flask version of the payment gateway for better serverless compatibility
"""
from flask import Flask, jsonify, request, render_template_string
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)

# Simplified version without external dependencies
class SimplePaymentGateway:
    def __init__(self):
        self.api_key = os.getenv("COINBASE_API_KEY", "demo_key")
        self.base_url = "https://api.commerce.coinbase.com"
        
    def get_pricing_tiers(self):
        return {
            "community": {"name": "Community", "price": 0, "crypto_discount": 0},
            "professional": {"name": "Professional", "price": 299, "crypto_discount": 10},
            "enterprise": {"name": "Enterprise", "price": 2999, "crypto_discount": 15},
            "quantum": {"name": "Quantum", "price": 9999, "crypto_discount": 20}
        }
    
    def create_payment(self, plan, amount):
        # In demo mode, return mock response
        if self.api_key == "demo_key":
            return {
                "data": {
                    "id": f"demo_charge_{plan}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "hosted_url": f"https://commerce.coinbase.com/charges/demo_{plan}",
                    "pricing": {"local": {"amount": str(amount), "currency": "USD"}},
                    "created_at": datetime.now().isoformat()
                }
            }
        
        # Real implementation would use requests to Coinbase API
        return {"error": "Real payments require COINBASE_API_KEY"}

gateway = SimplePaymentGateway()

@app.route('/')
def home():
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mycelium Payment Gateway</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .tier { border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 8px; }
            .price { font-size: 24px; font-weight: bold; color: #2d5aa0; }
            .discount { color: #28a745; font-weight: bold; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>🧬 Mycelium-EI-Lang Payment Portal</h1>
        <p>Bio-inspired programming with cryptocurrency payments</p>
        
        <div class="tier">
            <h3>Community (FREE)</h3>
            <div class="price">$0/month</div>
            <p>Basic bio-algorithms, Community support, 1,000 API calls</p>
            <button onclick="alert('Community tier is always free!')">Get Started</button>
        </div>
        
        <div class="tier">
            <h3>Professional</h3>
            <div class="price">$299/month <span class="discount">→ $269/month with crypto (10% off)</span></div>
            <p>Commercial algorithms, Priority support, GPU acceleration, 100,000 API calls</p>
            <button onclick="createPayment('professional', 269)">Pay with Crypto</button>
        </div>
        
        <div class="tier">
            <h3>Enterprise</h3>
            <div class="price">$2,999/month <span class="discount">→ $2,549/month with crypto (15% off)</span></div>
            <p>Unlimited algorithms, Dedicated support, Custom integrations, 10M API calls</p>
            <button onclick="createPayment('enterprise', 2549)">Pay with Crypto</button>
        </div>
        
        <div class="tier">
            <h3>Quantum</h3>
            <div class="price">$9,999/month <span class="discount">→ $7,999/month with crypto (20% off)</span></div>
            <p>Quantum computing, White-label licensing, Research partnerships, Unlimited API calls</p>
            <button onclick="createPayment('quantum', 7999)">Pay with Crypto</button>
        </div>
        
        <script>
            function createPayment(plan, amount) {
                fetch('/create-payment', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({plan: plan, amount: amount})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.data && data.data.hosted_url) {
                        window.open(data.data.hosted_url, '_blank');
                    } else {
                        alert('Payment creation: ' + JSON.stringify(data));
                    }
                })
                .catch(error => alert('Error: ' + error));
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gateway": "simplified_flask",
        "demo_mode": gateway.api_key == "demo_key"
    })

@app.route('/pricing')
def pricing():
    return jsonify(gateway.get_pricing_tiers())

@app.route('/create-payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    plan = data.get('plan')
    amount = data.get('amount')
    
    result = gateway.create_payment(plan, amount)
    return jsonify(result)

@app.route('/tokenomics')
def tokenomics():
    return jsonify({
        "token": "MYC",
        "total_supply": "1,000,000,000",
        "staking_tiers": {
            "bronze": {"min_stake": 1000, "apy": "8%"},
            "silver": {"min_stake": 10000, "apy": "12%"}, 
            "gold": {"min_stake": 100000, "apy": "18%"},
            "platinum": {"min_stake": 1000000, "apy": "25%"}
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)