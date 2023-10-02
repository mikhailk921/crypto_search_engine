# -*- coding: utf-8 -*-
# @file main.py
# @brief search engine code source

import copy
import datetime
import math
import sys
from threading import Thread

import websocket
import os
import json
import time
import traceback
import requests

from src.json_filter import json_filter, transform_result_data
from src.dextools_checker import get_dextools_data
from src.honeypot_checker import isHoneyPot
from src.tokensniffer_checker import get_tokensniffer_data
from src.table import draw_table

# tg bot api
BOT_KEY = ""

TMP_LOCAL_DIR = "tmp"
PAIR_ADDRESS_WAITING_LIST = []
WAITING_LIST_TIMER_UPDATE = time.time()

header_data = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.173',
    'origin': 'https://cs.money'}

header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    'origin': "https://dexscreener.com",
    'Host': "io.dexscreener.com",
    'Pragma': "no-cache"
}

cookie_string = '__cfduid=da97b059db0292806e2affdf9c3f4fd8b1593022325; _csrf=i8W6njc7hUXMOf4iQjiAxKg1; language=en; theme=darkTheme; pro_version=false; csgo_ses=1489162147d69debd9fe5d0ea2e445c87a117578d774502172d7151b89b82f7f; steamid=76561199068891508; avatar=https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg; username=andrewcrook232; thirdparty_token=06d04856ce6e334aa1368696df775e7ba0b1b898db135b0af0b5dc0fe001dd55; user_type=old; sellerid=6721648; type_device=desktop'

rec_data = {}
data_is_updated = False
is_processing = False
exit_flag = False


def print_statistics(total_length, processed_items):
    if total_length == 0:
        return
    total = math.floor((processed_items / total_length) * 100)
    sys.stdout.write('\r')
    sys.stdout.write(
        "[%-100s] %d%% total: %d  processed: %d  " % ('=' * int(total + 1), total, total_length, processed_items))
    sys.stdout.flush()


def end_print_statistics(total_length):
    print_statistics(total_length, total_length)
    print("\n")


def update_timestamp():
    tm = "Data status updated {0}".format(time.time())
    sys.stdout.write('\r')
    sys.stdout.write(tm)
    sys.stdout.flush()


def init(dir_name=TMP_LOCAL_DIR):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def on_message(ws, message):
    global rec_data
    global data_is_updated
    global is_processing
    if not message:
        return
    try:
        json_object = json.loads(message)
        if 'pairs' in json_object and not is_processing:
            rec_data = copy.deepcopy(json_object["pairs"])
            data_is_updated = True
            update_timestamp()
            with open('tmp/json_data.json', 'w') as f:
                json.dump(rec_data, f)
        elif False and len(PAIR_ADDRESS_WAITING_LIST) != 0 and time.time() - WAITING_LIST_TIMER_UPDATE > 300:
            run_pipline(PAIR_ADDRESS_WAITING_LIST, True)
            is_processing = False
            rec_data = copy.deepcopy(PAIR_ADDRESS_WAITING_LIST)

        if exit_flag:
            print("Ending web socket thread")
            ws.close()
    except Exception as e:
        print(e)


def run_web_socket_async():
    print("Start new web socket async thread")
    uri = "wss://io.dexscreener.com/dex/screener/pairs/h6/1?rankBy[key]=volume&rankBy[order]=desc&filters[pairAge][max]=24&filters[liquidity][min]=10000&filters[chainIds][0]=ethereum"
    print("url = {0}".format(uri))

    ws = websocket.WebSocketApp(uri, on_message=on_message, header=header_data, cookie=cookie_string)
    print("Connected")

    while not exit_flag:
        ws.run_forever(ping_timeout=20)

    print("Closing...")


def parse_data_from_file(path):
    with open(path, 'r') as json_file:
        return json.load(json_file)


def check_known_id(data):
    with open("checked_ids_storage.json", 'r') as validated_data_file:
        checked_ids_list = json.load(validated_data_file)
        return [i for i in data if not
        next((j for j in checked_ids_list if j["pairAddress"] == i["pairAddress"]), None)]


def add_more_known_id(data):
    if len(data) == 0:
        return
    checked_ids_list = []
    with open("checked_ids_storage.json", 'r') as validated_data_file:
        checked_ids_list = json.load(validated_data_file)
    print("Len before add knows ids {0}".format(len(checked_ids_list)))

    for item in data:
        for j in checked_ids_list:
            if j["pairAddress"] == item["pairAddress"]:
                break
        checked_ids_list.append({"pairAddress": item["pairAddress"], "isInterest": False})

    print("Len after add knows ids {0}".format(len(checked_ids_list)))

    with open('checked_ids_storage.json', 'w') as f:
        json.dump(checked_ids_list, f)


def run_pipline(data, is_rerun, run_forse=False):
    global is_processing
    is_processing = True
    if not run_forse and not is_rerun:
        data = check_known_id(data)
        add_more_known_id(data)

    if len(data) == 0 and not run_forse:
        return

    print("Start filtering")
    for item in data:
        print("\n*********************")
        print("{0} : {1} : {2}".format(datetime.datetime.now(), item["baseToken"]["name"], item["pairAddress"].lower()))
    data = json_filter(data)

    if len(data) == 0:
        return print("Base json check not passed")

    ### dextools
    print("Start dextool checker, length {0}".format(len(data)))
    counter = 0
    for item in data:
        time.sleep(1)
        print_statistics(len(data), counter)
        result = get_dextools_data(item["pairAddress"])
        item["dextools"] = result
        counter += 1
    end_print_statistics(len(data))

    print("Len before dextools filter {0}".format(len(data)))
    data = [i for i in data if
            not i["dextools"]["is_honeypot"] and not i["dextools"]["is_blacklisted"] and not i["dextools"][
                "anti_whale_modifiable"]]

    print("Len after dextools filter {0}".format(len(data)))

    if len(data) == 0:
        return print("dextools check not passed")

    ### honypot
    print("Start  honypot checker, length = {0}".format(len(data)))
    counter = 0
    for item in data:
        print_statistics(len(data), counter)
        time.sleep(1)
        if "address" in item["baseToken"]:
            result = isHoneyPot(item["baseToken"]["address"])  # item["pairAddress"])
            item["isHoneyPot"] = result
        counter += 1
    end_print_statistics(len(data))

    data = [i for i in data if not i["isHoneyPot"]]
    if len(data) == 0:
        return print("honypot check not passed")

    ### tokensniffer
    print("Start tokensniffer, length = {0}".format(len(data)))
    counter = 0
    for item in data:
        print_statistics(len(data), counter)
        time.sleep(1)
        result = get_tokensniffer_data(item["baseToken"]["address"], is_rerun)
        if result["is_forbidden"] or result["is_pending"]:
            print("tokensniffer check for baseToken {0} forbidden or pending. Adding to waiting list ...".format(
                item["baseToken"]["address"]))
            PAIR_ADDRESS_WAITING_LIST.append(item)
        item["tokensniffer"] = result
        counter += 1
    end_print_statistics(len(data))

    data = [i for i in data if "is_flagged" in i["tokensniffer"]
            and i["tokensniffer"]["adequate_liquidity"] > 5
            and not i["tokensniffer"]["has_pausable"]
            and not i["tokensniffer"]["has_mint"]
            and not i["tokensniffer"]["is_flagged"]
            and not i["tokensniffer"]["is_forbidden"]]

    if len(data) == 0:
        return print("tokensniffer check not passed")

    print("Result data length = {0}".format(len(data)))
    data = transform_result_data(data)
    with open('result.json', 'w') as f:
        json.dump(data, f)

    draw_table(data)

    def trigger_notification(data):
        for item in data:
            template = "----------NEW COIN-----------\n\nName: {0}\nAddress: {1}\nLiquidity: {2}\nisHoneypot: {3}\nisBlacklisted: {4}\nisFlagged: {5}\nisSellable: {6}\nTax: {7} / {8}\nisRisk: {9}\nBorn:{10}\nSocials: {11}\n\n{12}\n\n______________________".format(
                item["Name"], item["Address"], item["Liquidity"], item["is_honeypot"], item["is_blacklisted"],
                item["TSflag"], item["TSsellable"], item["Buy fee"], item["Sell fee"], item["Risk Level"],
                item["CreatedAt"], item["Social"], item["TSLink"])
            apiToken = BOT_KEY
            chatID = '-1001933070742'
            apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
            try:
                requests.post(apiURL, json={'chat_id': chatID, 'text': template})
            except Exception as e:
                print(e)

    if len(data) != 0:
        print("*** Start trigger notify")
        trigger_notification(data)
        print("*** notify was sent")


def stdin_listener():
    print("Start new stdin listener thread")
    global exit_flag

    while True:
        line = input()
        print("Input command: {0}".format(line))
        if line == "q":
            exit_flag = True
            print("Ending stdin listener thread")
            return


if __name__ == '__main__':

    a = {
        'a':1,
        'b':2,
        'c':3,
        'd':4
    }

    for i in a:
        print(i)
    exit()


    argv = None
    enable_command_monitor = True
    if len(sys.argv) > 1:
        argv = sys.argv[1]
    if argv is not None:
        enable_command_monitor = False

    init()
    chainId = "ethereum"
    data = None
    run_forse = False
    is_rerun = False

    web_socket_thread = Thread(target=run_web_socket_async)
    command_line_monitor_thread = Thread(target=stdin_listener)

    web_socket_thread.start()
    if enable_command_monitor is True:
        command_line_monitor_thread.start()

    while not exit_flag:
        if data_is_updated:
            run_pipline(rec_data, is_rerun)
            data_is_updated = False
            is_processing = False
        time.sleep(1)

    web_socket_thread.join()
    if enable_command_monitor is True:
        command_line_monitor_thread.join()

    # data = parse_data_from_file("tmp/json_data.json")
