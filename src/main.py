# -*- coding: utf-8 -*-
## @file main.py
# @brief search engine code source

import asyncio
from threading import Thread

import websocket
import os
import json
import time
import traceback

from json_filter import json_filter
from dextools_checker import get_dextools_data
from honeypot_ckecker import isHoneyPot
from tokensniffer_checker import get_tokensniffer_data


TMP_LOCAL_DIR = "tmp"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.173', 'origin': 'https://cs.money'}
cookie_string = '__cfduid=da97b059db0292806e2affdf9c3f4fd8b1593022325; _csrf=i8W6njc7hUXMOf4iQjiAxKg1; language=en; theme=darkTheme; pro_version=false; csgo_ses=1489162147d69debd9fe5d0ea2e445c87a117578d774502172d7151b89b82f7f; steamid=76561199068891508; avatar=https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg; username=andrewcrook232; thirdparty_token=06d04856ce6e334aa1368696df775e7ba0b1b898db135b0af0b5dc0fe001dd55; user_type=old; sellerid=6721648; type_device=desktop'

rec_data = {}


def init(dir_name=TMP_LOCAL_DIR):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def on_message(ws, message):
    global rec_data
    if not message:
        return
    try:
        json_object = json.loads(message)
        if not rec_data and 'pairs' in json_object.keys() and len(json_object["pairs"]) != 0:
            print(json_object)
            print("Saving rec data ...")
            rec_data = json_object["pairs"]
            print("Saved")
            ws.close()
    except():
        print(traceback.format_exc())


async def run_web_socket_async():
    print("It's new thread")
    uri = "wss://io.dexscreener.com/dex/screener/pairs/h6/1?rankBy[key]=volume&rankBy[order]=desc&filters[pairAge][max]=24&filters[liquidity][min]=10000&filters[chainIds][0]=ethereum"
    print("url = {0}".format(uri))

    ws = websocket.WebSocketApp(uri, on_message=on_message, header=headers, cookie=cookie_string)
    print("Connected")

    ws.run_forever(ping_timeout=20)

    print("Closing...")
    ws.close()
    print("Connection closed")


async def run_async():
    print("Start new thread")
    # async_task = asyncio.get_event_loop().create_task(run_web_socket_async())
    #async_task = asyncio.create_task(run_web_socket_async())
    await run_web_socket_async()

    while not rec_data:
        time.sleep(5)
        print("Waiting data ...")

    #print("data = {0}".format(rec_data))

    with open('tmp/json_data.json', 'w') as f:
        json.dump(rec_data, f)


def run_web_socket_sync():
    global rec_data
    uri = "wss://io.dexscreener.com/dex/screener/pairs/h6/1?rankBy[key]=volume&rankBy[order]=desc&filters[pairAge][max]=24&filters[liquidity][min]=10000&filters[chainIds][0]=ethereum"

    ws = websocket.WebSocket()
    ws.connect(uri, header=headers, cookie=cookie_string)
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
                print(json_object)
                print("Saving rec data ...")
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


if __name__ == '__main__':
    init()
    chainId = "ethereum"
    mode = None
    mode = "sync"
    data = None
    run_forse = True

    if mode == "async":
        asyncio.run(run_async())
        data = rec_data
    elif mode == "sync":
        data = run_sync()
    else:
        data = parse_data_from_file("from_file", "tmp/json_data.json")

    if not run_forse:
        print("Len before check knows ids {0}".format(len(data)))
        data = check_known_id(data)
        print("Len after check knows ids {0}".format(len(data)))
        add_more_known_id(data)

    if len(data) == 0 and not run_forse:
        print("No new coins received. All received coins have already been verified. Script completing")
        exit(0)


    print("Start filtering")
    data = json_filter(data)


    ### dextools
    for item in data:
        time.sleep(1)
        result = get_dextools_data(item["pairAddress"])#, mode="file")
        item["dextools"] = result

    data = [i for i in data if "top10_bauer" in i["dextools"]]
    with open('tmp/dexscreener_and_dextools_data.json', 'w') as f:
        json.dump(data, f)
    #print(json.dumps(data[0]))


    ### honypot
    print("Start  honypot checker, length = {0}".format(len(data)))
    for item in data:
        time.sleep(1)
        result = isHoneyPot(item["pairAddress"])
        item["isHoneyPot"] = result

    data = [i for i in data if not i["isHoneyPot"]]

    with open('tmp/honeypot_data.json', 'w') as f:
        json.dump(data, f)


    ### tokensniffer
    print("Start tokensniffer, length = {0}".format(len(data)))
    for item in data:
        time.sleep(1)
        result = get_tokensniffer_data(item["baseToken"]["address"])
        print(result)
        item["tokensniffer"] = result

    data = [i for i in data if "is_flagged" in i["tokensniffer"]]

    print("Result data length = {0}".format(len(data)))
    print(json.dumps(data))



