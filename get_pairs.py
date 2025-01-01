import requests

response = requests.get("https://api.kraken.com/0/public/AssetPairs")
asset_pairs = response.json()["result"]
for pair in asset_pairs:
    if "BT" in pair and "USDT" in pair:
        print(pair)
