# -*- coding: utf-8 -*-
## @file main.py
# @brief search engine code source


import sys

from src.dextools_checker import get_dextools_data
from src.honeypot_checker import isHoneyPot
from src.tokensniffer_checker import get_tokensniffer_data

# BOT_API_KEY = 5986303026:AAEvJ3Z8PV_1VofFY94Ktq6-0_X38vg5Hbg


def run_pipline(pair_address):
    result = {"pair_address": pair_address}
    # dextools
    print("Start dextool checker")
    counter = 0

    dextools_data = get_dextools_data(pair_address)
    result["dextools"] = dextools_data

    ### honypot
    print("Start honypot checker")
    honey_pot_data = isHoneyPot(result["dextools"]["token_address"])
    result["isHoneyPot"] = honey_pot_data

    ### tokensniffer
    print("Start tokensniffer")
    tokensniffer_data = get_tokensniffer_data(result["dextools"]["token_address"])
    result["tokensniffer"] = tokensniffer_data

    ###
    ### Filtering

    # dextools
    print("Start dextools filter")

    if result["dextools"]["is_honeypot"] or result["dextools"]["is_blacklisted"] \
            or result["dextools"]["anti_whale_modifiable"]:
        print("dextools filter not passed")
        return False

    # honypot
    if result["isHoneyPot"]:
        print("honypot filter not passed")
        return False

    ### tokensniffer
    if result["tokensniffer"]["adequate_liquidity"] < 5 or result["tokensniffer"]["has_pausable"] or result["tokensniffer"]["has_mint"]:
        print("tokensniffer filter not passed")
        return False

    print("Verification passed successfully")
    return True


if __name__ == "__main__":
    #pair_address = int(sys.argv[1])
    pair_address = "0xbaea270bbfed2f34a045b5bc6b65626f653f2999"

    result = run_pipline(pair_address)
