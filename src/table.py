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

data = [
    ["1", "OWNER", "Liquidity", "M.cap","Tax","Age","Website","Telegram","LP Lock","Total Count","Gas","WARNING"],
    ["2", "OWNER", "Liquidity", "M.cap","Tax","Age","Website","Telegram","LP Lock","Total Count","Gas","WARNING"],
    ["3", "OWNER", "Liquidity", "M.cap","Tax","Age","Website","Telegram","LP Lock","Total Count","Gas","WARNING"],
]

columns = [
 "ETH", "OWNER", "Liquidity", "M.cap","Tax","Age","Website","Telegram","LP Lock","Total Count","Gas","WARNING"
 ]

print(tabulate(data,headers=columns,showindex="always"))
