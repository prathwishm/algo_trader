from kite_ext_new import KiteExt_new
from config import kite_username, kite_password, kite_pin
from telegram_bot import telegram_bot_sendtext
import datetime, pytz, time, os

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

telegram_bot_sendtext('Testing algo_trader...')

acc_price = kite.ltp('NSE:ACC')['NSE:ACC']['last_price']
acc_order_price = acc_price - (acc_price*0.05)
placed_order_id = kite.place_order(tradingsymbol='ACC',
                            exchange=kite.EXCHANGE_NSE,
                            transaction_type=kite.TRANSACTION_TYPE_BUY,
                            quantity=1,
                            order_type=kite.ORDER_TYPE_LIMIT,
                            price=acc_order_price,
                            product=kite.PRODUCT_MIS,
                            variety=kite.VARIETY_AMO)

print('placed order id is', placed_order_id)
print('Cancelling order in 15 seconds')
time.sleep(15)
kite.cancel_order(variety = kite.VARIETY_AMO, order_id = placed_order_id)