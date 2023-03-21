# -*- coding: utf-8 -*-
## @file main.py
# @brief tokensniffer checker code source
import json
from time import sleep

import requests


def get_tokensniffer_data(baseTokenAddress, is_rerun=False):
    url = "https://tokensniffer.com/api/v2/tokens/1/{0}?include_metrics=true&include_tests=false&apikey=dafe4651dc541b6516e142219c947cf9a8e70884".format(baseTokenAddress)
    headers = {"accept": "application/json"}

    counter = 0
    forbidden_counter = 0
    result = None
    response = None
    while counter < 30 and forbidden_counter < 10:
        counter += 1
        response = requests.get(url, headers=headers)
        text = response.text
        #print(text)

        if text == "Contract not found":
            print("\ntokensniffer: Contract {0} not found...".format(baseTokenAddress))
            return {
                "is_flagged": False,
                "is_sellable": False,  # need true
                "buy_fee": 0,
                "sell_fee": 0,
                "is_source_verified": False,
                "is_ownership_renounced": False,
                "lock_balance": 0,
                "deployer_balance": 0,
                #
                "riskLevel": "",
                # initial liquidity ...
                "score": 0,
                "owner_balance": 0,
                "adequate_liquidity": 0,
                "has_pausable": True,
                "has_mint": True,
                "is_forbidden": False,
                "is_pending": False,
            }
        if "html" in text:
            forbidden_counter += 1
            sleep(3)
            continue
        result = json.loads(text)
        #print(json.dumps(result))

        if "status" in result and result["status"] == "pending":
            #print("tokensniffer: status pending, restart...")
            sleep(1)
            continue
        break

    if result is None or ("status" in result and result["status"] == "pending"):
        print("\ntokensniffer result is None...  {0}".format(response.text))
        return {
            "is_flagged": False,
            "is_sellable": False,  # need true
            "buy_fee": 0,
            "sell_fee": 0,
            "is_source_verified": False,
            "is_ownership_renounced": False,
            "lock_balance": 0,
            "deployer_balance": 0,
            #
            "riskLevel": "",
            # initial liquidity ...
            "score": 0,
            "owner_balance": 0,
            "adequate_liquidity": 0,
            "has_pausable": True,
            "has_mint": True,
            "is_forbidden": True if "html" in response.text else False,
            "is_pending": True if ("status" in result and result["status"] == "pending") else False,
        }

    return {
        "is_flagged": result["is_flagged"],
        "is_sellable": result["swap_simulation"]["is_sellable"], # need true
        "buy_fee": result["swap_simulation"]["buy_fee"],
        "sell_fee": result["swap_simulation"]["sell_fee"],
        "is_source_verified": result["contract"]["is_source_verified"],
        "is_ownership_renounced": result["permissions"]["is_ownership_renounced"],
        "lock_balance": result["balances"]["lock_balance"],
        "deployer_balance": result["balances"]["deployer_balance"] / 10e12,
        #
        "riskLevel": result["riskLevel"],
        # initial liquidity ...
        "score": result["score"],
        "owner_balance": result["balances"]["owner_balance"],
        "adequate_liquidity": result["pools"][0]["base_reserve"] if len(result["pools"]) > 0 else 0,
        "has_pausable": result["contract"]["has_pausable"] if "has_pausable" in result["contract"] else False,
        "has_mint": result["contract"]["has_mint"] if "has_mint" in result["contract"] else False,
        "is_forbidden": False,
        "is_pending": False,
    }


if __name__ == '__main__':
    mode = "file"
    data = {}

    data = get_tokensniffer_data("0x4d7529faa257f121909f1077532f0e9adca9f441")
    #data = get_tokensniffer_data("0xBAa79dC2BD6a7c387C1Fbdceab6E1031B74fAA6B")
    #data = get_tokensniffer_data("0xbaa79dc2bd6a7c387c1fbdceab6e1031b74faa6b")

    print(json.dumps(data))


