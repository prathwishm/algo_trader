from login_using_selenium import login_using_selenium
from telegram_bot import telegram_bot_sendtext
from ticker_service import Ticker_class
from orders import Class_Orders
from functions_collections import Kite_functions
from config import kite_username, kite_password, kite_pin
from kite_ext_new import KiteExt_new
from redis import Redis
import datetime, pytz, time, os
import traceback
import subprocess
from straddle_strategy3 import straddles
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('main.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(file_handler)

holidays = ["2022-01-26", "2022-03-1", "2022-03-18", "2022-04-14", "2022-04-15", "2022-05-03", "2022-08-09", "2022-08-15", "2022-08-31", "2022-10-05", "2022-10-24", "2022-10-26", "2022-11-08"]
#If today is a holiday or Saturday/Sunday quit
if str(datetime.date.today()) in holidays or datetime.date.today().isoweekday() > 5:
    telegram_bot_sendtext('Today is a trading holiday. Exiting...')
    quit()

redis_server = subprocess.Popen('redis-server --port 6380', shell=True)
redis_obj = Redis(host='localhost', port=6380, decode_responses=True)
telegram_bot_sendtext('Starting Algo...')

kite = KiteExt_new()

for _ in range(3):
    selenium_login_status = login_using_selenium()
    if selenium_login_status:
        break

enctoken_modification_time = os.path.getmtime('enctoken.txt')
# Converting the time in seconds to a timestamp
enctoken_modification_time_stamp = time.ctime(enctoken_modification_time)

if int(enctoken_modification_time_stamp[8:10]) == datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).day:
    with open('enctoken.txt', 'r') as enctoken_file:
        enctoken = enctoken_file.read()
        kite.login_using_enctoken(kite_username, enctoken, None)

else:
    logger.info("Logging in using Kiteext")
    telegram_bot_sendtext("Logging in using Kiteext")
    kite.login_with_credentials(userid=kite_username, password=kite_password, pin=kite_pin)

ticker = Ticker_class(kite=kite, tokens = [256265, 260105])
kite_func = Kite_functions(kite)
orders_obj = Class_Orders(kite = kite, redis_obj = redis_obj, kite_functions = kite_func)

#straddles_obj = straddles(kite=kite, kite_func= kite_func, orders_obj = orders_obj, margin=1)
straddles_obj = straddles(kite=kite, kite_func= kite_func, orders_obj = orders_obj, redis_obj = redis_obj, ticker = ticker, margin=1)

#ticker.tokens = straddles_obj.nf_bnf_option_tokens
ticker.start_ticker()
time.sleep(5)

current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
error_count = 0
while current_dt.hour <= 15 and not (current_dt.hour >= 15 and current_dt.minute >= 30):
    try:
        current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
        if current_dt.hour == 15 and current_dt.minute >= 21:
            #Exit from all open positions at 3:15.
            # kite_day_positions_list = kite_func.get_positions_list()['net']
            # for each_position in kite_day_positions_list:
            #     try:
            #         if each_position['quantity'] != 0 and each_position['product'] == 'MIS':
            #             stock = each_position['tradingsymbol']
            #             exit_quantity = abs(each_position['quantity'])
            #             exit_type = "sell" if each_position['quantity'] > 0 else "buy"
            #             if exit_quantity > 0:
            #                 orders_obj.exit_position(stock, exit_type, exit_quantity)

            #                 telegram_bot_sendtext(f"Exiting from {stock} at 3:15")
            #     except Exception as e:
            #         print("Unexpected error while exiting positions at 3:15. Error: "+str(e))
            #         traceback.print_exc()
            break

        straddles_obj.main()
        time.sleep(2)


    except Exception as e:
        logger.exception("Unexpected error in main while loop. Error: "+str(e))
        traceback.print_exc()
        error_count += 1
        if error_count >10:
            break

    except KeyboardInterrupt:
        logger.info('\nKeyboard exception received. Exiting.')
        break

logger.info('Stopping Websocket')
ticker.kws.stop()

redis_cli = subprocess.Popen('redis-cli -p 6380', shell=True,
                        stdin =subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, bufsize=0, universal_newlines=True,)

redis_cli.stdin.write("flushdb \n")
time.sleep(2)
redis_server.kill()

telegram_bot_sendtext('Algo Shutting down...')