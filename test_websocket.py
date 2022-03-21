from kite_ext_new import KiteExt_new
from config import kite_username, kite_password, kite_pin
from telegram_bot import telegram_bot_sendtext
import datetime, pytz, time, os
from ticker_service import Ticker_class
from redis import Redis
from subprocess import Popen

redis_server = Popen('redis-server')
time.sleep(1)

kite = KiteExt_new()

#selenium_login_status = login_using_selenium()

enctoken_modification_time = os.path.getmtime('enctoken.txt')
# Converting the time in seconds to a timestamp
enctoken_modification_time_stamp = time.ctime(enctoken_modification_time)

if int(enctoken_modification_time_stamp[8:10]) == datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).day:
    with open('enctoken.txt', 'r') as enctoken_file:
        enctoken = enctoken_file.read()
        kite.login_using_enctoken(kite_username, enctoken, None)

else:
    print("Logging in using Kiteext")
    kite.login_with_credentials(userid=kite_username, password=kite_password, pin=kite_pin)

telegram_bot_sendtext('Testing algo_trader webscoket...')

ticker = Ticker_class(kite=kite, tokens = [256265, 260105])

ticker.start_ticker()
time.sleep(5)

redis_obj = Redis(host='127.0.0.1', port=6379, decode_responses=True)

for i in range(5):
    banknifty_ltp = eval(redis_obj.get(str(260105)))
    nifty_ltp = eval(redis_obj.get(str(256265)))
    print(f"Nifty {nifty_ltp} \nBanknifty {banknifty_ltp}")
    time.sleep(1)

redis_server.kill()