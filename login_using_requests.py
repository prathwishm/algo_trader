import requests
import json
import traceback
from config import kite_username, kite_password, kite_pin
from telegram_bot import telegram_bot_sendtext

def login_to_kite():
    try:
        r = requests.post('https://kite.zerodha.com/api/login', data={
            'user_id': kite_username,
            'password': kite_password
        })

        r2 = requests.post('https://kite.zerodha.com/api/twofa', data={
            'request_id': r.json()['data']['request_id'],
            'twofa_value': kite_pin,
            'user_id': r.json()['data']['user_id']
        })

        login_cookies = [
            {'domain': "kite.zerodha.com",'name': c.name, 'path': c.path, 'secure': True, 'value': c.value}
            for c in r2.cookies
        ]

        telegram_bot_sendtext('[' + str(json.dumps(login_cookies)) + ']', filter_text=False)

        with open('enctoken.txt', 'w+') as wr:
            wr.write(r2.cookies.get_dict()['enctoken'])
            print("Enctoken Updated")

        return True

    except Exception as e:
        telegram_bot_sendtext("Error while logging in using Selenium. Error: "+str(e))
        print("Error while logging in using Selenium. Error: "+str(e))
        traceback.print_exc()
        return False