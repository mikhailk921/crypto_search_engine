# -*- coding: utf-8 -*-
## @file main.py
# @brief tokensniffer checker code source
import json
from time import sleep

import requests


def get_tokensniffer_data(baseTokenAddress):
    url = "https://tokensniffer.com/api/v2/tokens/1/{0}?include_metrics=true&include_tests=false&apikey=dafe4651dc541b6516e142219c947cf9a8e70884".format(baseTokenAddress)
    headers = {"accept": "application/json"}

    counter = 0
    result = None
    while counter < 10:
        counter += 1
        response = requests.get(url, headers=headers)
        text = response.text
        #print(text)

        if text == "Contract not found":
            print("\ntokensniffer: Contract {0} not found...".format(baseTokenAddress))
            return {}
        if "html" in text:
            sleep(1)
            continue
        result = json.loads(text)
        if "status" in result.keys() and result["status"] == "pending":
            #print("tokensniffer: status pending, restart...")
            sleep(1)
            continue
        break

    if result is None:
        return {}

    return {
        "is_flagged": False if result["is_flagged"] == "false" else True,
        "is_sellable": False if result["swap_simulation"]["is_sellable"] == "false" else True, # need true
        "buy_fee": result["swap_simulation"]["buy_fee"],
        "sell_fee": result["swap_simulation"]["sell_fee"],
        "is_source_verified": False if result["contract"]["is_source_verified"] == "false" else True,
        "is_ownership_renounced": False if result["permissions"]["is_ownership_renounced"] == "false" else True,
        "lock_balance": result["balances"]["lock_balance"],
        "deployer_balance": result["balances"]["deployer_balance"] / 10e12,
        #
        "riskLevel": result["riskLevel"],
        # initial liquidity ...
        "score": result["score"],
        "owner_balance": result["balances"]["owner_balance"],
    }


if __name__ == '__main__':
    mode = "file"
    data = {}

    #data = get_tokensniffer_data("0x64aBE0fA0F44f688D26321b611686aa289780411")
    #data = get_tokensniffer_data("0xBAa79dC2BD6a7c387C1Fbdceab6E1031B74fAA6B")
    data = get_tokensniffer_data("0xbaa79dc2bd6a7c387c1fbdceab6e1031b74faa6b")

    print(data)


