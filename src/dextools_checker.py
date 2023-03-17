# -*- coding: utf-8 -*-
## @file main.py
# @brief dextools checker code source

import requests
import json


def get_json_from_dextools(pair_address):
    uri = "https://www.dextools.io/chain-ethereum/api/Pancakeswap/1/pairexplorer?v=2.47.1&pair={0}&ts=1671461472-0&h=1".format(pair_address)

    headers = {
        'cookie': '_pk_id.4.b299=8b297bde9046c6c3.1678695768.;_pk_ref.4.b299=["","",1678776376,"https://www.google.com/"];_pk_ses.4.b299=1;__cf_bm=8h6lzEfoMDjEHC05qtU3j.I3QwF3ptJqVuLTd5y9wUQ-1678778151-0-ATA7nQcdrmalQiJcKIxIPl2C6/2OWzWmo9gRfaycDz+NWZlkhseY/fO69tRKhgGg89kkpFMjuBfx0RSVCQf+4vS2qx8Pl9u3f5nxPoXkQ1xJOSa4Mkk6J5KYvbzwiehDIA==',
        'origin': 'https://www.dextools.io/',
        'referer': 'https://www.dextools.io/app/en/bnb/pair-explorer',
        'content-type': 'text/plain;charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    x = requests.get(uri, headers=headers)
    #print(x.text)
    result = json.loads(x.text)['result']
    #print(json.dumps(result))
    return result


def sort_by_top10_bayer(data):
    sorted_data = [i for i in data if i['type'] == "buy"]
    #sorted_data = OrderedDict(sorted(sorted_data, key=lambda i: int(i['amountETH'])))
    sorted_data.sort(key= lambda i: i['amountETH'], reverse=True)
    return sorted_data[0:10]

def sort_by_top10_seller(data):
    sorted_data = [i for i in data if i['type'] == "sell"]
    sorted_data.sort(key= lambda i: i['amountETH'], reverse=True)
    return sorted_data[0:10]

def get_count_with_less_005(data):
    count = 0
    for item in data:
        if item['amountETH'] <= 0.05:
            count += 1
    return count


def get_audit_data(pair_address):
    uri = "https://www.dextools.io/shared/data/pair?address={0}&chain=ether&audit=true".format(pair_address)
    headers = {
        'cookie': '_pk_id.4.b299=8b297bde9046c6c3.1678695768.;_pk_ref.4.b299=["","",1678776376,"https://www.google.com/"];_pk_ses.4.b299=1;__cf_bm=8h6lzEfoMDjEHC05qtU3j.I3QwF3ptJqVuLTd5y9wUQ-1678778151-0-ATA7nQcdrmalQiJcKIxIPl2C6/2OWzWmo9gRfaycDz+NWZlkhseY/fO69tRKhgGg89kkpFMjuBfx0RSVCQf+4vS2qx8Pl9u3f5nxPoXkQ1xJOSa4Mkk6J5KYvbzwiehDIA==',
        'origin': 'https://www.dextools.io/',
        'referer': 'https://www.dextools.io/app/en/bnb/pair-explorer',
        'content-type': 'text/plain;charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    x = requests.get(uri, headers=headers)
    result = json.loads(x.text)
    # with open('tmp/dextools_audit_data.json', 'w') as f:
    #     json.dump(result, f)
    if "data" in result.keys():
        result = result['data']
    else:
        #print("Empty json with social links: {0}".format(uri))
        return {"count": 0, "social": []}
    if not result or len(result) == 0 or not result[0]["token"] or not result[0]["token"]["links"]:
        print("Incorrect json with social links")
        return {"count": 0, "social": []}
    links = result[0]["token"]["links"]
    #print(json.dumps(links))

    count = len({k: v for k, v in links.items() if v != ""}.keys())

    is_honeypot = True
    is_blacklisted = True
    anti_whale_modifiable = True
    if "external" in result[0]["token"]["audit"] and "is_honeypot" in result[0]["token"]["audit"]["external"]["goplus"]:
        is_honeypot = False if result[0]["token"]["audit"]["external"]["goplus"]["is_honeypot"] == "0" else True
        is_blacklisted = False if result[0]["token"]["audit"]["external"]["goplus"]["is_blacklisted"] == "0" else True
        anti_whale_modifiable = False if result[0]["token"]["audit"]["external"]["goplus"]["anti_whale_modifiable"] == "0" else True

    return {
        "count": count,
        "social": [v for k, v in links.items() if v != ""],
        "pair_address": pair_address,
        "token_address": result[0]["id"]["token"],
        "is_honeypot": is_honeypot,
        "is_blacklisted": is_blacklisted,
        "anti_whale_modifiable": anti_whale_modifiable,
        }

def parse_data_from_file(path=None):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
        #print(data)
        return data


def get_dextools_data(pair_address, mode="web"):
    data = []
    if mode == "web":
        data = get_json_from_dextools(pair_address)
        if len(data) == 0:
            return {
                "top10_bauer": [],
                "top10_seller": [],
                "count_less_005": 0,
                "total_count": len(data),
                "links_count": 0,
                "links": [],
                "is_honeypot": None,
                "is_blacklisted": None,
                "anti_whale_modifiable": None,
                "pair_address": pair_address,
                "token_address": None,
            }
        #with open('tmp/dextools_data.json', 'w') as f:
        #    json.dump(data, f)
    else:
        data = parse_data_from_file("tmp/dextools_data.json")

    top10_bauer = sort_by_top10_bayer(data)
    #print(json.dumps(top10_bauer))

    top10_seller = sort_by_top10_seller(data)
    #print(json.dumps(top10_seller))

    count_less_005 = get_count_with_less_005(data)
    #print("count_less_05 = {0}".format(count_less_05))

    audit = get_audit_data(pair_address)
    #print("audit = {0}".format(audit))

    return {
        "top10_bauer": top10_bauer,
        "top10_seller": top10_seller,
        "count_less_005": count_less_005,
        "total_count": len(data),
        "links_count": audit["count"],
        "links": audit["social"],
        "is_honeypot": audit["is_honeypot"] if "is_honeypot" in audit else None,
        "is_blacklisted": audit["is_blacklisted"] if "is_blacklisted" in audit else None,
        "anti_whale_modifiable": audit["anti_whale_modifiable"] if "anti_whale_modifiable" in audit else None,
        "pair_address": audit["pair_address"],
        "token_address": audit["token_address"],
    }


if __name__ == '__main__':
    mode = "web"

    data = get_dextools_data("0xd8adCC692ed752c8B7c5337d7eB8Fe0A13b2996c", mode)
    #data = get_dextools_data("0xd3a9a2ebd567030bb1f1c3fb21a4a203d51c246b", mode)    # work
    #data = get_dextools_data("0xf3033c15162e9565ba39098d42cefd95b1dbd601")
    print(json.dumps(data))

## remove if "is_honeypot": "1",
## remove if "is_blacklisted": "1",
## remove if "anti_whale_modifiable": "1",
##