# -*- coding: utf-8 -*-
## @file main.py
# @brief search engine code source


import sys
import telebot

from src.dextools_checker import get_dextools_data
from src.honeypot_checker import isHoneyPot
from src.tokensniffer_checker import get_tokensniffer_data

BOT_KEY = "5986303026:AAEvJ3Z8PV_1VofFY94Ktq6-0_X38vg5Hbg"
bot = telebot.TeleBot(BOT_KEY, parse_mode=None)

def run_pipline(pair_address):
    pair_address = pair_address.lower()
    result = {"pair_address": pair_address}
    # dextools
    print("Start dextool checker")
    counter = 0

    dextools_data = get_dextools_data(pair_address)
    result["dextools"] = dextools_data
    if result["dextools"]["token_address"] is None:
        return "Checking result: Not passed. Not found token address"

    ### honypot
    print("Start honypot checker")
    #print(result["dextools"]["token_address"])
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
        return "Checking result: Not passed dextools"

    # honeypot
    if result["isHoneyPot"]:
        print("honypot filter not passed")
        return "Checking result: Not passed honeypot"

    ### tokensniffer
    if result["tokensniffer"]["adequate_liquidity"] < 5 or result["tokensniffer"]["has_pausable"] or result["tokensniffer"]["has_mint"]:
        print("tokensniffer filter not passed")
        return "Checking result: Not passed tokensniffer"

    print("Verification passed successfully")
    return "Checking result: Passed"


# Running a check for single coin
@bot.message_handler(commands=['check'])
def handle_message_for_check(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'You should use check with address in one line: For example: "/check 0x0000000001"')
        return 
    pair_address = message_text[1]
    bot.reply_to(message, f'Checking....')
    results = run_pipline(pair_address)
    return bot.reply_to(message, '{0}'.format(results))


if __name__ == "__main__":
    bot.infinity_polling()

#     #pair_address = int(sys.argv[1])
#      pair_address = "0x6046C0d755FbB2AeeBf69b8b3134fCFC780B2203"
#      result = run_pipline(pair_address)
