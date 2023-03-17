import requests
import json
import re
import math
import time

# url = "https://api.etherscan.io/api?module=account&action=balance&address=0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e&tag=latest&apikey=W13I1AY4ZVU59GRDG2T96W3AGP7TPV71KG"
# babur = 0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e

# BOT_API_KEY = 5850868426:AAFXBNuqUKunw0fVTKybMYrdGrnosn1G2w4
# url = "https://api.etherscan.io/api?module=account&action=txlist&address=0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e&startblock=0&endblock=99999999&offset=200&page=1&sort=asc&apikey=W13I1AY4ZVU59GRDG2T96W3AGP7TPV71KG"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.173', 
    'origin': 'https://etherscan.io'
    }
# cookie_string = '__cfduid=da97b059db0292806e2affdf9c3f4fd8b1593022325; _csrf=i8W6njc7hUXMOf4iQjiAxKg1; language=en; theme=darkTheme; pro_version=false; csgo_ses=1489162147d69debd9fe5d0ea2e445c87a117578d774502172d7151b89b82f7f; steamid=76561199068891508; avatar=https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg; username=andrewcrook232; thirdparty_token=06d04856ce6e334aa1368696df775e7ba0b1b898db135b0af0b5dc0fe001dd55; user_type=old; sellerid=6721648; type_device=desktop'

# https://etherscan.io/txs?a=0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e&ps=100&p=3
def transactions_count(wallet: str = None) -> list:
    assert(wallet is not None)
    response = requests.get('https://etherscan.io/txs?a={0}'.format(wallet), headers=headers)
    response_parsed = response.content.decode()
    pages = int(re.findall("total\s+of\s+(.*?)\s+transactions\s+found",response_parsed)[0].replace(',', ''))
    pages = math.ceil(pages/200)
    print(pages)


def transactions(wallet: str = None) -> list:
    for x in range(19):
        print('Current page is = {0}'.format(x+1))
        assert(wallet is not None)
        url_params = {
            'module': 'account',
            'action': 'txlist',
            'address': wallet,
            'startblock': 0,
            'endblock': 99999999,
            'page': x,
            'offset': 200,
            'sort': 'asc',
            'apikey': "W13I1AY4ZVU59GRDG2T96W3AGP7TPV71KG" # Use your API key here!
        }
        response = requests.get('https://api.etherscan.io/api', params=url_params)
        response_parsed = json.loads(response.content)
        assert(response_parsed['message'] == 'OK')
        txs = response_parsed['result']
        database = [ json.dumps({'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp'], 'type':tx["functionName"]}) \
            for tx in txs if "swap" in tx["functionName"].lower() or "multicall" in tx["functionName"]]
        with open('accounts.json', 'a') as f:
            json.dump(database, f)
        time.sleep(2)


def json_filtering(database):
    database_filtered = []
    for i in database:
        database_filtered.append([

        ])


# transactions('0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e')
# transactions_count('0xb71b13b85d2c094b0fdec64ab891b5bf5f110a8e')