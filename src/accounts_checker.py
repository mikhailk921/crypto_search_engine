import requests

# url = "https://api.etherscan.io/api?module=account&action=balance&address=0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e&tag=latest&apikey=W13I1AY4ZVU59GRDG2T96W3AGP7TPV71KG"

url = "https://api.etherscan.io/api?module=account&action=txlist&address=0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e&startblock=0&endblock=99999999&offset=200&page=1&sort=asc&apikey=W13I1AY4ZVU59GRDG2T96W3AGP7TPV71KG"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)