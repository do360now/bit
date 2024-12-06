import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Get API credentials from environment variables.
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Ensure critical environment variables are set.
if not API_KEY or not API_SECRET:
    raise ValueError("API_KEY or API_SECRET is missing. Please check your environment variables.")

# API endpoint domain. Default to Kraken's public API if not set.
API_DOMAIN: str = os.getenv("API_DOMAIN", "https://api.kraken.com")

# Allocation strategy for portfolio management:
# These values represent the fraction of your total holdings allocated to each category.
ALLOCATIONS = {
    'HODL': float(os.getenv("ALLOC_HODL", 0.85)),
    'YIELD': float(os.getenv("ALLOC_YIELD", 0.0)),
    'TRADING': float(os.getenv("ALLOC_TRADING", 0.15)),
}

# Initial total BTC balance. This could represent a starting amount of BTC the bot manages.
TOTAL_BTC: float = float(os.getenv("TOTAL_BTC", 0.0014623402))

# Minimum trading volume, to ensure orders are not too small. Adjust this based on exchange minimums.
MIN_TRADE_VOLUME: float = float(os.getenv("MIN_TRADE_VOLUME", 0.00015))

# A global cooldown period (in seconds) between trades to prevent over-trading or rate-limit issues.
# Default is 15 minutes.
GLOBAL_TRADE_COOLDOWN: int = int(os.getenv("GLOBAL_TRADE_COOLDOWN", 900))
