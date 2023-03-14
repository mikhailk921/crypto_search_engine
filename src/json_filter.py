# -*- coding: utf-8 -*-
## @file main.py
# @brief json filter code source


import os
import json


def filter_by_liquidity(data):
    return [i for i in data if i["liquidity"]["usd"] > 7000]


def filter_by_sale(data):
    return [i for i in data if i["txns"]["h24"]["sells"] > 0]


def compare_dynamic_data(data):
    return [i for i in data if i["priceChange"]["h24"] != 0
            and i["priceChange"]["h6"] != 0
            and i["priceChange"]["h1"] != 0
            and i["priceChange"]["m5"] != 0]


def json_filter(data):
    print("Filtering by liquidity. Start data length = {0}".format(len(data)))
    data = filter_by_liquidity(data)
    print("Filtering by sale. Start data length = {0}".format(len(data)))
    data = filter_by_sale(data)
    print("Filtering by comparing dynamic. Start data length = {0}".format(len(data)))
    data = compare_dynamic_data(data)

    print("Final data length = {0}".format(len(data)))
    return data


def transform_data(data):
    return data

