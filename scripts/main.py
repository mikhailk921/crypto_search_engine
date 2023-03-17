# -*- coding: utf-8 -*-
## @file main.py
# @brief search engine code source

import asyncio
import copy
import math
import sys
from threading import Thread

import websocket
import os
import json
import time
import traceback

from src.json_filter import json_filter, transform_result_data
from src.dextools_checker import get_dextools_data
from src.honeypot_checker import isHoneyPot
from src.tokensniffer_checker import get_tokensniffer_data
from src.table import draw_table

# BOT_API_KEY = 6022347804:AAFVpXBH3Pc-PCO3luaBECH8meD3F-FNdOQ
TMP_LOCAL_DIR = "tmp"

header_data = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.173', 'origin': 'https://cs.money'}

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
    # the exact output you're looking for:
    sys.stdout.write(
        "[%-100s] %d%% total: %d  processed: %d  "
        % ('=' * int(total + 1), total, total_length, processed_items))
    sys.stdout.flush()


def update_timestamp():
    tm = "Data status updated {0}".format(time.time())
    sys.stdout.write('\r')
    # the exact output you're looking for:
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
            #print(json_object)
            rec_data = copy.deepcopy(json_object["pairs"])
            data_is_updated = True
            update_timestamp()
            with open('tmp/json_data.json', 'w') as f:
                json.dump(rec_data, f)
        #else:
            #print("Not received a new data or processing ... {0)  {1}".format(is_processing, message))

        if exit_flag:
            print("Ending web socket thread")
            ws.close()
    except():
        print(traceback.format_exc())


def run_web_socket_async():
    print("It's new thread")
    uri = "wss://io.dexscreener.com/dex/screener/pairs/h6/1?rankBy[key]=volume&rankBy[order]=desc&filters[pairAge][max]=24&filters[liquidity][min]=10000&filters[chainIds][0]=ethereum"
    print("url = {0}".format(uri))

    ws = websocket.WebSocketApp(uri, on_message=on_message, header=header_data, cookie=cookie_string)
    print("Connected")

    while not exit_flag:
        ws.run_forever(ping_timeout=20)

    print("Closing...")
    #ws.close()
    #print("Connection closed")


def run_async():
    print("Start new web socket async thread")
    # async_task = asyncio.get_event_loop().create_task(run_web_socket_async())
    #async_task = asyncio.create_task(run_web_socket_async())
    run_web_socket_async()

    # while not rec_data:
    #     time.sleep(5)
    #     print("Waiting data ...")
    #
    # #print("data = {0}".format(rec_data))
    #
    # with open('tmp/json_data.json', 'w') as f:
    #     json.dump(rec_data, f)


def run_web_socket_sync():
    global rec_data
    uri = "wss://io.dexscreener.com/dex/screener/pairs/h6/1?rankBy[key]=volume&rankBy[order]=desc&filters[pairAge][max]=24&filters[liquidity][min]=10000&filters[chainIds][0]=ethereum"
    #uri = "wss://io.dexscreener.com/dex/screener/pairs/h6/1?filters[chainIds][0]=ethereum"
    ws = websocket.WebSocket()
    ws.connect(uri, headers=header_data, cookie=cookie_string)
    print("Connected")

    while True:
        print("Waiting ...")
        time.sleep(1)
        message = ws.recv()
        if not message:
            continue
        try:
            json_object = json.loads(message)
            if not rec_data and 'pairs' in json_object.keys():
                #print(json_object)
                rec_data = json_object["pairs"]
                print("Saved")
                break
        except():
            print(traceback.format_exc())

    print("Closing socket...")
    ws.close()
    print("Connection closed")


def run_sync():
    run_web_socket_sync()
    #print("data = {0}". format(rec_data))
    with open('tmp/json_data.json', 'w') as f:
        json.dump(rec_data, f)
    return rec_data


def parse_data_from_file(mode, path=None):
    if mode == "from_file":
        with open(path, 'r') as json_file:
            data = json.load(json_file)
            #print(data)
            return data


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
        print("checked_ids_list {0}".format(len(checked_ids_list)))

    print("Len after add knows ids {0}".format(len(checked_ids_list)))

    with open('checked_ids_storage.json', 'w') as f:
        json.dump(checked_ids_list, f)


def run_pipline(data, mode, run_forse=False):
    global is_processing
    is_processing = True
    if not run_forse:
        if mode != "async":
            print("Len before check knows ids {0}".format(len(data)))
        data = check_known_id(data)
        if mode != "async":
            print("Len after check knows ids {0}".format(len(data)))
        add_more_known_id(data)

    if len(data) == 0 and not run_forse:
        if mode != "async":
            print("No new coins received. All received coins have already been verified. Script completing")
        return
        #exit(0)
    # print(json.dumps(data))

    print("Start filtering")
    if mode == "async":
        for item in data:
            print("{0} :  {1}".format(item["baseToken"]["name"], item["pairAddress"]))
    data = json_filter(data)
    # print(json.dumps(data[0]))

    ### dextools
    print("Start dextool checker")
    counter = 0
    for item in data:
        time.sleep(1)
        print_statistics(len(data), counter)
        result = get_dextools_data(item["pairAddress"])  # , mode="file")
        item["dextools"] = result
        counter += 1
    print_statistics(len(data), counter)
    print("\n")

    data = [i for i in data if "top10_bauer" in i["dextools"]]

    print("Len before dextools filter {0}".format(len(data)))
    data = [i for i in data if
            not i["dextools"]["is_honeypot"] and not i["dextools"]["is_blacklisted"] and not i["dextools"][
                "anti_whale_modifiable"]]
    print("Len after dextools filter {0}".format(len(data)))

    with open('tmp/dexscreener_and_dextools_data.json', 'w') as f:
        json.dump(data, f)
    # print(json.dumps(data[0]))

    ### honypot
    print("Start  honypot checker, length = {0}".format(len(data)))
    counter = 0
    for item in data:
        print_statistics(len(data), counter)
        time.sleep(1)
        result = isHoneyPot(item["baseToken"]["address"])  # item["pairAddress"])
        item["isHoneyPot"] = result
        counter += 1
    print_statistics(len(data), counter)
    print("\n")

    data = [i for i in data if not i["isHoneyPot"]]

    with open('tmp/honeypot_data.json', 'w') as f:
        json.dump(data, f)

    ### tokensniffer
    print("Start tokensniffer, length = {0}".format(len(data)))
    counter = 0
    for item in data:
        print_statistics(len(data), counter)
        time.sleep(1)
        result = get_tokensniffer_data(item["baseToken"]["address"])
        item["tokensniffer"] = result
        counter += 1
    print_statistics(len(data), counter)
    print("\n")

    data = [i for i in data if "is_flagged" in i["tokensniffer"]
            and i["tokensniffer"]["adequate_liquidity"] > 5
            and not i["tokensniffer"]["has_pausable"]
            and not i["tokensniffer"]["has_mint"]]

    print("Result data length = {0}".format(len(data)))
    # if len(data) != 0:
    #    print(json.dumps(data[0]))
    data = transform_result_data(data)
    with open('result.json', 'w') as f:
        json.dump(data, f)

    draw_table(data)

    def trigger_notification(data):
        pass
    if len(data) != 0:
        trigger_notification(data)


def command_line_monitor():
    print("Start new command monitor thread")
    global exit_flag
    while True:
        line = input()
        print("Input command: {0}".format(line))
        if line == "q":
            exit_flag = True

            print("Ending command monitor thread")
            return


if __name__ == '__main__':

    init()
    chainId = "ethereum"
    mode = None
    mode = "async"
    new_thread = None
    data = None
    run_forse = False

    if mode == "async":
        #asyncio.run(run_async())
        web_socket_thread = Thread(target=run_async)
        command_line_monitor_thread = Thread(target=command_line_monitor)

        web_socket_thread.start()
        command_line_monitor_thread.start()

        while not exit_flag:
            if data_is_updated:
                run_pipline(rec_data, mode)
                data_is_updated = False
                is_processing = False
            time.sleep(1)

        web_socket_thread.join()
        command_line_monitor_thread.join()

    elif mode == "sync":
        data = run_sync()
        run_pipline(data, mode)
    else:
        data = parse_data_from_file("from_file", "tmp/json_data.json")



    #print(json.dumps(data))



