from kite_ext_new import KiteExt_new
from config import kite_username, kite_password, kite_pin
from telegram_bot import telegram_bot_sendtext
import datetime, pytz, time, os
#from ticker_service import Ticker_class
# from redis import Redis
# from subprocess import Popen

# redis_server = Popen('redis-server --port 6380', shell=True)
# time.sleep(1)

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

# ticker = Ticker_class(kite=kite, tokens = [256265, 260105])

# ticker.start_ticker()
# time.sleep(5)

# redis_obj = Redis(host='localhost', port=6380, decode_responses=True)

# for i in range(5):
#     banknifty_ltp = eval(redis_obj.get(str(260105)))
#     #banknifty_ltp = ticker.ltp_dict[260105]
#     nifty_ltp = eval(redis_obj.get(str(256265)))
#     #nifty_ltp = ticker.ltp_dict[256265]
#     print(f"Nifty {nifty_ltp} \nBanknifty {banknifty_ltp}")
#     time.sleep(1)

# redis_server.kill()

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    print("Ticks: {}".format(ticks))

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe([738561, 5633])

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, [738561])

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws = kite.ticker()
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()