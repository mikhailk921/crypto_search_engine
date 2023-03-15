# -*- coding: utf-8 -*-
## @file main.py
# @brief honeypot checker code source

import requests
import json


def isHoneyPot(pair_address):
#pair_address = '0x67f0A54A019E1De8d6Bc5B52E48F09d76e815F99';
    uri = "https://aywt3wreda.execute-api.eu-west-1.amazonaws.com/default/IsHoneypot?chain=eth&token={0}".format(pair_address)
    headers = {
        'cookie': '_pk_id.4.b299=8b297bde9046c6c3.1678695768.;_pk_ref.4.b299=["","",1678776376,"https://www.google.com/"];_pk_ses.4.b299=1;__cf_bm=8h6lzEfoMDjEHC05qtU3j.I3QwF3ptJqVuLTd5y9wUQ-1678778151-0-ATA7nQcdrmalQiJcKIxIPl2C6/2OWzWmo9gRfaycDz+NWZlkhseY/fO69tRKhgGg89kkpFMjuBfx0RSVCQf+4vS2qx8Pl9u3f5nxPoXkQ1xJOSa4Mkk6J5KYvbzwiehDIA==',
        'origin': 'https://www.honeypot.is',
        'referer': 'https://www.honeypot.is',
        'content-type': 'text/plain;charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    x = requests.get(uri, headers=headers)

    if 'IsHoneypot' not in json.dumps(json.loads(x.text)):
        print("Incorrect json: {0}".format(uri))

    isHoneyPot = json.dumps(json.loads(x.text)['IsHoneypot']) == "true"
    #print("isHoneyPot = {0};  {1}".format(isHoneyPot, pair_address))

    return isHoneyPot


if __name__ == '__main__':
    mode = "file"
    data = {}

    #result = isHoneyPot("0x67f0A54A019E1De8d6Bc5B52E48F09d76e815F99")
    result = isHoneyPot("0x514910771af9ca656af840dff83e8264ecf986ca")

    print(result)
