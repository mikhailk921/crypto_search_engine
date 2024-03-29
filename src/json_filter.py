# -*- coding: utf-8 -*-
## @file main.py
# @brief json filter code source


import os
import json
from datetime import datetime


def filter_by_liquidity(data):
    return [i for i in data if i["liquidity"]["usd"] > 7000]


def filter_by_sale(data):
    return data
    #return [i for i in data if i["txns"]["h24"]["sells"] > 0]


def compare_dynamic_data(data):
    return data
    # return [i for i in data if i["priceChange"]["h24"] != 0
    #         and i["priceChange"]["h6"] != 0
    #         and i["priceChange"]["h1"] != 0]
    # and i["priceChange"]["m5"] != 0]


def json_filter(data):
    print("Filtering by liquidity. Start data length = {0}".format(len(data)))
    data = filter_by_liquidity(data)
    print("Filtering by sale. Start data length = {0}".format(len(data)))
    data = filter_by_sale(data)
    print("Filtering by comparing dynamic. Start data length = {0}".format(len(data)))
    data = compare_dynamic_data(data)

    print("Final data length = {0}".format(len(data)))
    result = []
    for item in data:
        item["baseToken"]["address"] = item["baseToken"]["address"].lower()
        item["quoteToken"]["address"] = item["quoteToken"]["address"].lower()
        result.append({
            "chainId": item["chainId"],
            "pairAddress": item["pairAddress"].lower(),
            "baseToken": item["baseToken"],
            "quoteToken": item["quoteToken"],
            "price": item["price"],
            "priceUsd": item["priceUsd"],
            "txns": item["txns"],
            "buyers": item["buyers"],
            "sellers": item["sellers"],
            "priceChange": item["priceChange"],
            "liquidity": item["liquidity"],
            "pairCreatedAt": item["pairCreatedAt"],
        })

    return result


def convert_data_types_to_str(value):
    if value is None:
        return "null"
    elif value is True:
        return "true"
    elif value is False:
        return "false"
    else:
        return value


def transform_result_data(data):
    result = []
    for i in data:
        result.append({
            "Name": i["baseToken"]["name"],
            "Address": i["baseToken"]["address"],
            "Liquidity": i["liquidity"]["usd"],
            "Total/Less": "{0} / {1}".format(i["dextools"]["total_count"], i["dextools"]["count_less_005"]),
            "Social": ", ".join(i["dextools"]["links"]),
            "is_honeypot": convert_data_types_to_str(i["dextools"]["is_honeypot"]),
            "is_blacklisted": convert_data_types_to_str(i["dextools"]["is_blacklisted"]),
            "anti_whale_modifiable": convert_data_types_to_str(i["dextools"]["anti_whale_modifiable"]),
            "Honeypot": convert_data_types_to_str(i["isHoneyPot"]),
            "TSflag": convert_data_types_to_str(i["tokensniffer"]["is_flagged"]),
            "TSsellable": convert_data_types_to_str(i["tokensniffer"]["is_sellable"]),
            "Buy fee": i["tokensniffer"]["buy_fee"],
            "Sell fee": i["tokensniffer"]["sell_fee"],
            "Risk Level": i["tokensniffer"]["riskLevel"],
            "Score": i["tokensniffer"]["score"],
            "CreatedAt": datetime.utcfromtimestamp(i["pairCreatedAt"]/1000).strftime('%Y-%m-%d %H:%M:%S'),
            "TSLink": "https://tokensniffer.com/token/eth/{0}".format(i["baseToken"]["address"]),
        })

    return result


if __name__ == '__main__':

    result = datetime.utcfromtimestamp(1678872383000/1000).strftime('%Y-%m-%d %H:%M:%S')

    print(result)

