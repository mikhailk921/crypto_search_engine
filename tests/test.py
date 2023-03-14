import websocket
import json
import time
import traceback

uri = 'wss://io.dexscreener.com/dex/screener/pairs/h6/1?rankBy[key]=volume&rankBy[order]=desc&filters[pairAge][max]=24&filters[liquidity][min]=10000&filters[chainIds][0]=ethereum'


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.173', 'cookie': '__cfduid=da97b059db0292806e2affdf9c3f4fd8b1593022325; _csrf=i8W6njc7hUXMOf4iQjiAxKg1; language=en; theme=darkTheme; pro_version=false; csgo_ses=1489162147d69debd9fe5d0ea2e445c87a117578d774502172d7151b89b82f7f; steamid=76561199068891508; avatar=https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg; username=andrewcrook232; thirdparty_token=06d04856ce6e334aa1368696df775e7ba0b1b898db135b0af0b5dc0fe001dd55; user_type=old; sellerid=6721648; type_device=desktop', 'origin': 'https://cs.money'}
cookie_string = headers['cookie']
del headers['cookie']
header_without_cookie = headers

rec_data = None


def on_message(ws, message):
    global rec_data
    try:
        #print(message)
        json_object = json.loads(message)
        if not rec_data and 'pairs' in json_object.keys():
            print(json_object)
            print("Saving rec data ...")
            rec_data = json_object
    except():
        print(traceback.format_exc())


def start_ws():
    global rec_data

    ws = websocket.WebSocketApp(uri, on_message=on_message, header=header_without_cookie, cookie=cookie_string)
    print("Connected")
    count = 0

    while not rec_data or count < 40:
        count += 1
        ws.run_forever(ping_timeout=5)

        print("Reload")
        time.sleep(20)

    ws.stop_ping()
    print("Closing...")
    ws.close()
    print("Connection closed")
    #except:
    #    print(traceback.format_exc())

    print(rec_data)


if __name__ == "__main__":
    start_ws()

