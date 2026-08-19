from flask import Flask, render_template_string, request
import redis
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# Prometheus metrics
ATM_TRANSACTIONS = Counter('atm_transactions_total', 'Total ATM transactions', ['type'])

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinTech ATM & Analytics Dashboard</title>
    <!-- استدعاء خط Poppins العصري -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
        }
        body {
            background: linear-gradient(135deg, #0f172a, #1e1b4b, #311042);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow-x: hidden;
        }
        .container {
            width: 90%;
            max-width: 900px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            text-align: center;
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            font-size: 2.2rem;
            margin-bottom: 30px;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
        }
        .card {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 25px;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        .card:hover {
            transform: translateY(-8px);
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 10px 30px rgba(56, 189, 248, 0.2);
        }
        .card h3 {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .card .amount {
            font-size: 2rem;
            font-weight: 700;
            color: #38bdf8;
        }
        .card.balance .amount {
            color: #34d399;
        }
        .actions-form {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .btn {
            background: linear-gradient(135deg, #0284c7, #6366f1);
            color: white;
            border: none;
            padding: 14px 28px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
        }
        .btn:hover {
            opacity: 0.9;
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }
        .btn-withdraw {
            background: linear-gradient(135deg, #e11d48, #9333ea);
            box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4);
        }
        .footer {
            margin-top: 20px;
            font-size: 0.85rem;
            color: #64748b;
            letter-spacing: 0.5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💳 FinTech ATM Analytics</h1>
        
        <div class="cards-grid">
            <div class="card">
                <h3>Total Deposits</h3>
                <div class="amount">${{ deposits or 0 }}</div>
            </div>
            <div class="card">
                <h3>Total Withdrawals</h3>
                <div class="amount">${{ withdrawals or 0 }}</div>
            </div>
            <div class="card balance">
                <h3>Current Balance</h3>
                <div class="amount">${{ balance or 0 }}</div>
            </div>
        </div>

        <form method="POST" class="actions-form">
            <button type="submit" name="action" value="deposit" class="btn">➕ Simulate Deposit ($100)</button>
            <button type="submit" name="action" value="withdraw" class="btn btn-withdraw">➖ Simulate Withdraw ($50)</button>
        </form>

        <div class="footer">
            Microservices Architecture • Redis Caching • Prometheus & Grafana Monitored
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'deposit':
            r.incrby('deposits', 100)
            r.incrby('balance', 100)
            ATM_TRANSACTIONS.labels(type='deposit').inc()
        elif action == 'withdraw':
            r.incrby('withdrawals', 50)
            r.decrby('balance', 50)
            ATM_TRANSACTIONS.labels(type='withdraw').inc()
            
    return render_template_string(HTML_TEMPLATE, 
                                  deposits=r.get('deposits'), 
                                  withdrawals=r.get('withdrawals'), 
                                  balance=r.get('balance'))

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
