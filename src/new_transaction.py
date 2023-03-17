import telebot
import os
import requests
import json
import time
import threading

def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func
ETHERSCAN_KEY = "W13I1AY4ZVU59GRDG2T96W3AGP7TPV71KG"
BOT_KEY = "6243919336:AAHe1b9sbX2wHHghAEdVeoUfMC4j7iQKTUM" 
SUBSCRIPTIONS_FILE_PATH = 'subscriptions.json'
# Create the bot
bot = telebot.TeleBot(BOT_KEY, parse_mode=None)
subscriptions = {}
# Read the cached config on the system
if os.path.exists(SUBSCRIPTIONS_FILE_PATH):
    with open(SUBSCRIPTIONS_FILE_PATH) as file:
        subscriptions = json.load(file)
def transactions(wallet: str = None) -> list:
    assert(wallet is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 10,
        'sort': 'asc',
        'apikey': ETHERSCAN_KEY
    }
    
    response = requests.get('https://api.etherscan.io/api', params=url_params)
    response_parsed = json.loads(response.content)
    assert(response_parsed['message'] == 'OK')
    txs = response_parsed['result']
    return [ json.dumps({'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp'], 'type':tx["functionName"]}) \
            for tx in txs if "swap" in tx["functionName"].lower() or "multicall" in tx["functionName"].lower()]
def update_subscriptions(chat_id, wallet) -> bool:
    global subscriptions
    try:
        txs = transactions(wallet)
        if chat_id not in subscriptions.keys():
            subscriptions[chat_id] = {}
        subscriptions[chat_id][wallet] = txs
        return True
    except:
        return False
# Show the user the wallets they're listening to
@bot.message_handler(commands=['get_stalking_list'])
def handle_get_listening_wallets(message):
    if message.chat.id in subscriptions.keys():
        bot.reply_to(message, f'You are currently stalking to events from: {subscriptions[message.chat.id].keys()}')
    else:
        bot.reply_to(message, 'You are not stalking to any wallet transactions!')
# Add a new wallet to listen to
@bot.message_handler(commands=['add_stalking_wallet'])
def handle_add_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address.')
        return 
    wallet_addr = message_text[1]
    if not update_subscriptions(message.chat.id, wallet_addr):
        bot.reply_to(message, f'Failed to add the wallet to stalking list! Is it a real address?')
        print(subscriptions)
        return
    bot.reply_to(message, f'You are now stalking to events from the following wallets: {subscriptions[message.chat.id].keys()}')
# Remove a wallet that is being listened to
@bot.message_handler(commands=['remove_stalking_wallet'])
def handle_remove_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address.')
        return 
    wallet_addr = message_text[1]
    if wallet_addr in subscriptions[message.chat.id].keys():
        del subscriptions[message.chat.id][wallet_addr]
        bot.reply_to(message, f'Wallet address {wallet_addr} now disabled for stalking!')
    else:
        bot.reply_to(message, f'Could not find wallet address  - did you ever stalking? address: {wallet_addr}')
# Get the latest transaction from a list of transactions, based on timestamp
def get_latest_tx(txs: list) -> int:
    return max(txs,key=lambda tx: int(tx['timestamp']))
# Format a transaction dict item to printable string
def format_tx(tx: dict) -> str:
    return f'From: {tx["from"]}, To: {tx["to"]}, Amount: {tx["value"]}'
# Background poll Etherscan for all wallets and update users
@background
def infinity_wallet_updates():
    while True:
        for chat in subscriptions:
            for wallet in subscriptions[chat]:
                previous_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                print(previous_latest_tx)
                update_subscriptions(chat, wallet)
                current_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                if int(current_latest_tx['timestamp']) > int(previous_latest_tx['timestamp']):
                    bot.send_message(chat, f'New transactions happened for {wallet}!')
                    [bot.send_message(chat, format_tx(tx)) for tx in \
                        filter(lambda tx: int(tx['timestamp']) > previous_latest_tx, subscriptions[chat][wallet])]
        with open(SUBSCRIPTIONS_FILE_PATH, 'w') as file:
            json.dump(subscriptions, file)
        time.sleep(60*3)
# Run the bot!
infinity_wallet_updates()
bot.infinity_polling()