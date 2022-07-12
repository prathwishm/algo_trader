from telegram_bot import telegram_bot_sendtext
from celery import Celery
from redis import Redis
from threading import Thread
import logging
import datetime
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('ticker_error_celery.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(file_handler)

app = Celery('tasks', broker='redis://127.0.0.1:6380/0', backend='redis://127.0.0.1:6380/1')

r = Redis(host='localhost', port=6380, decode_responses=True)

ticker_dict = {}

def add_ticker_tokens(tokens_list):
    global ticker_dict
    for each_token in tokens_list:
        ticker_dict[each_token] = []

@app.task
def insert_ticks(ticks):
    global ticker_dict
    try:
        for tick in ticks:
            ticker_token = tick['instrument_token']
            try:
                #print(tick)
                if ticker_token in [256265, 260105, 257801]:
                    r.set(ticker_token, tick['last_price'])
                elif not (ticker_dict[ticker_token][-1] == tick['volume_traded'] and ticker_dict[ticker_token][-2] == tick['last_price']):
                    if type(tick['last_trade_time']) == str:
                        tick['last_trade_time'] = datetime.datetime.strptime(tick['last_trade_time'], '%Y-%m-%dT%H:%M:%S')
                    vals = [tick['last_trade_time'], tick['last_price'], tick['volume_traded']]
                    ticker_dict[ticker_token] = vals

                    r.set(ticker_token, tick['last_price'])
                    r.set(str(ticker_token) + '_depth', str(tick['depth']))
                    r.rpush(str(ticker_token) + '_data', str(vals))

            except IndexError:
                print(ticker_token, "not in dict.")
                if type(tick['last_trade_time']) == datetime.datetime:
                    if (tick['last_trade_time'].hour >= 9 and tick['last_trade_time'].minute >= 15) or tick['last_trade_time'].hour >= 10:
                        vals = [tick['last_trade_time'], tick['last_price'], tick['volume_traded']]
                        ticker_dict[ticker_token] = vals
                else:
                    print(f'tick last_trade_time is not datetime object. The type is {type(tick["last_trade_time"])}. The value is {tick["last_trade_time"]}')
                    tick['last_trade_time'] = datetime.datetime.strptime(tick['last_trade_time'], '%Y-%m-%dT%H:%M:%S')
                    vals = [tick['last_trade_time'], tick['last_price'], tick['volume_traded']]
                    ticker_dict[ticker_token] = vals

            except KeyError as key:
                logger.exception(f"Unexpected  KeyError in ticker for {key}")
                ticker_dict[ticker_token] = []

            except Exception as e:
                logger.exception("Unexpected error in ticker. Error: "+str(e))
                telegram_bot_sendtext("Unexpected error in ticker. Error: "+str(e))

    except Exception as e:
        logger.exception("Unexpected error in ticker. Error: "+str(e))
        telegram_bot_sendtext("Unexpected error in ticker. Error: "+str(e))


def insert_ticks2(ticks):
    x = Thread(target = insert_ticks, args = [ticks])
    x.start()
        
if __name__ == '__main__':
    from subprocess import Popen
    import time

    redis_server = Popen('redis-server --port 6380', shell=True)
    time.sleep(1)
    ticks = [{'instrument_token': 256265,'last_price': 17.45,},
            {'instrument_token': 260105,'last_price': 37.45,},
            {'instrument_token': 257801,'last_price': 27.45,}]
    insert_ticks2(ticks)
    print("Data inserted into redis successfully")
    redis_server.kill()