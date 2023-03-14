# -*- coding: utf-8 -*-
## @file main.py
# @brief dextools checker code source
from collections import OrderedDict

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

def get_count_with_less_05(data):
    count = 0
    for item in data:
        if item['amountETH'] <= 0.5:
            count += 1
    return count


def get_links_count(pair_address):
    uri = "https://www.dextools.io/shared/data/pair?address={0}&chain=ether&audit=false".format(pair_address)
    headers = {
        'cookie': '_pk_id.4.b299=8b297bde9046c6c3.1678695768.;_pk_ref.4.b299=["","",1678776376,"https://www.google.com/"];_pk_ses.4.b299=1;__cf_bm=8h6lzEfoMDjEHC05qtU3j.I3QwF3ptJqVuLTd5y9wUQ-1678778151-0-ATA7nQcdrmalQiJcKIxIPl2C6/2OWzWmo9gRfaycDz+NWZlkhseY/fO69tRKhgGg89kkpFMjuBfx0RSVCQf+4vS2qx8Pl9u3f5nxPoXkQ1xJOSa4Mkk6J5KYvbzwiehDIA==',
        'origin': 'https://www.dextools.io/',
        'referer': 'https://www.dextools.io/app/en/bnb/pair-explorer',
        'content-type': 'text/plain;charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    x = requests.get(uri, headers=headers)
    result = json.loads(x.text)
    if "data" in result.keys():
        result = result['data']
    else:
        #print("Empty json with social links: {0}".format(uri))
        return 0
    if not result or len(result) == 0 or not result[0]["token"] or not result[0]["token"]["links"]:
        print("Incorrect json with social links")
        return 0
    links = result[0]["token"]["links"]
    #print(json.dumps(links))
    count = len({k: v for k, v in links.items() if v != ""}.keys())
    return count

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
            return {}
        with open('tmp/dextools_data.json', 'w') as f:
            json.dump(data, f)
    else:
        data = parse_data_from_file("tmp/dextools_data.json")

    top10_bauer = sort_by_top10_bayer(data)
    #print(json.dumps(top10_bauer))

    top10_seller = sort_by_top10_seller(data)
    #print(json.dumps(top10_seller))

    count_less_05 = get_count_with_less_05(data)
    #print("count_less_05 = {0}".format(count_less_05))

    links_count = get_links_count(pair_address)
    #print("links_count = {0}".format(links_count))

    return {
        "top10_bauer": top10_bauer,
        "top10_seller": top10_seller,
        "count_less_05": count_less_05,
        "total_count": len(data),
        "links_count": links_count,
    }


if __name__ == '__main__':
    mode = "file"
    data = {}

    data = get_dextools_data("0x194aa72806d46b83311773d5415e05199ebb6b0c", mode)
    #data = get_dextools_data("0x4b729d5d871057f3a9c424792729217cde72410d")


