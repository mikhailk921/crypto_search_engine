# -*- coding: utf-8 -*-
## @file main.py
# @brief honeypot checker code source


from tabulate import tabulate

main_thing = "...data.items"
buy_fee = "5%"
sell_fee = "7%"
lock_balance = "lock_balance"
score = "90"
owner_balance ="1ETH"
top10_bauer = "top_10_buyer"
top10_seller = "top10_seller"
count_less_05 = "count_less_05"
total_count = "len(data)"
links_count = "links_count"


def draw_table(data):

    data_list = []

    for i in data:
        data_list.append([
            i["Name"], i["Address"], i["Liquidity"], i["Total/Less"], i["Social"],
            i["Honeypot"], i["TSflag"], i["TSsellable"], i["Buy fee"], i["Sell fee"],
            i["Risk Level"], i["Score"], i["CreatedAt"], i["TSLink"],
        ])

    columns = [
        "Name", "Address", "Liquidity", "Total/Less", "Social", "Honeypot", "TSflag", "TSsellable", "Buy fee",
        "Sell fee", "Risk Level", "Score", "CreatedAt", "TSLink"
     ]

    print(tabulate(data_list, headers=columns, showindex="always"))


if __name__ == '__main__':

    draw_table({})


