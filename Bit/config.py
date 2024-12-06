import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("API_KEY or API_SECRET is missing. Please check your environment variables.")

API_DOMAIN = os.getenv("API_DOMAIN", "https://api.kraken.com")

# Allocation strategy for portfolio management
ALLOCATIONS = {
    'HODL': float(os.getenv("ALLOC_HODL", 0.85)),
    'YIELD': float(os.getenv("ALLOC_YIELD", 0.0)),
    'TRADING': float(os.getenv("ALLOC_TRADING", 0.15)),
}

# Initial BTC balance
TOTAL_BTC = float(os.getenv("TOTAL_BTC", 0.00368))

# Minimum trading volume to avoid very small trades
MIN_TRADE_VOLUME = float(os.getenv("MIN_TRADE_VOLUME", 0.00015))

# Cooldown period in seconds between trades (default 15 minutes)
GLOBAL_TRADE_COOLDOWN = int(os.getenv("GLOBAL_TRADE_COOLDOWN", 900))

# Current Portfolio Snapshot (for reference)
CURRENT_PORTFOLIO_SNAPSHOT = {
    'EUR': {
        'percentage': 0.5770,
        'amount_eur': 1218.04,  # Assumed unchanged
    },
    'BTC': {
        'percentage': 0.1340,
        'price_eur': 92757.60,
        'amount_btc_total': 0.00368,
        'primary_btc': 0.00368 * 0.8,  # 0.002944 BTC
        'secondary_btc': 0.00368 * 0.2,  # 0.000736 BTC
        'amount_eur': 0.00368 * 92757.60  # ≈ 341.57 EUR
    }
}


SLEEP_DURATION = 300  # 5 minutes
