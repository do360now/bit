import requests

response = requests.get('https://api.kraken.com/0/public/Assets')
assets = response.json().get('result', {})
print(assets)
