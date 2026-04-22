# Binance Futures Testnet Trading Bot

A clean, structured Python CLI trading bot that places **Market**, **Limit**, and **Stop-Market** orders on the Binance Futures Testnet (USDT-M).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance API wrapper (HMAC signing, HTTP requests)
│   ├── orders.py          # Order placement logic + output formatting
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logger setup (file + console)
├── logs/                  # Auto-created; daily log files written here
├── cli.py                 # CLI entry point (argparse)
├── .env.example           # Copy to .env and fill in your keys
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Keys
1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with GitHub
3. Click **API Key** → **Generate Key** → choose **System Generated**
4. Copy your **API Key** and **Secret Key** (secret shown only once!)

### 2. Clone & Install

```bash
git clone https://github.com/your-username/trading_bot.git
cd trading_bot

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env`:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

---

## How to Run

### Market Order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit Order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 80000
```

### Stop-Market Order (Bonus)
```bash
python cli.py --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.1 --price 3000
```

---

## Sample Output

```
-------------------------------------------------------
         ORDER REQUEST SUMMARY
-------------------------------------------------------
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
-------------------------------------------------------
         ORDER RESPONSE
-------------------------------------------------------
  Order ID   : 123456789
  Status     : FILLED
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Orig Qty   : 0.01
  Exec Qty   : 0.01
  Avg Price  : 84321.50
-------------------------------------------------------
  Order placed successfully!
-------------------------------------------------------
```

---

## Logs

Logs are written to `logs/trading_bot_YYYYMMDD.log` automatically.

Each log entry includes timestamp, log level, and full request/response details.

---

