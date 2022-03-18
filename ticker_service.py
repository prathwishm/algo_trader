from update_ticks_using_celery import insert_ticks, add_ticker_tokens, insert_ticks2
from telegram_bot import telegram_bot_sendtext
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('ticker_error.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(file_handler)

class Ticker_class():
    """
    Class to consume tick by tick data.
    Stores the latest price, volume and depth in redis.

    microsecond should be added to "last_trade_time" to ensure that mutiple ticks
    having same timestamp are handled while converting tick data to candles.

    latest tick data is compared with last stored tick data of that instrument to prevent duplicate ticks
    """
    
    def __init__(self, kite, tokens):
        self.kite = kite
        self.tokens = tokens
        self.websocket_is_open = False

    def start_ticker(self):

        add_ticker_tokens(self.tokens)
 
        def on_ticks(ws,ticks):
            #insert_ticks.delay(ticks)
            insert_ticks2(ticks)
            #print(ticks)

        def on_connect(ws,response):
            self.websocket_is_open = True
            ws.subscribe(self.tokens)
            ws.set_mode(ws.MODE_FULL,self.tokens)
            logger.info(f"Successfully connected. Response: {response}")
            telegram_bot_sendtext('Successfully Connected to Websocket')
            
        def on_close(ws, code, reason):
            self.websocket_is_open = False
            logger.info(f'Closing Websocket. The code is {code} . Reason is {reason}')
            telegram_bot_sendtext(f'Closing Websocket. The code is {code} . Reason is {reason}')

        def on_error(ws, code, reason):
            logger.error(f'Error in websocket. Error code is {code} . Reason is {reason}')
            telegram_bot_sendtext(f'Error in websocket. Error code is {code} . Reason is {reason}')

        def on_reconnect(ws, attempts_count):
            logger.info(f"Reconnecting: {attempts_count}")

        def on_noreconnect(ws):
            logger.info("Reconnect failed.")

        self.kws = self.kite.ticker()
        self.kws.on_ticks = on_ticks
        self.kws.on_connect = on_connect
        self.kws.on_close = on_close
        self.kws.on_error = on_error
        self.kws.on_reconnect = on_reconnect
        self.kws.on_noreconnect = on_noreconnect
        self.kws.connect(threaded=True)

    def subscribe_tokens(self, tokens_list):
        if type(tokens_list) == list and len(tokens_list) > 0:
            add_ticker_tokens(tokens_list)
            for each_token in tokens_list:
                if each_token not in self.tokens:
                    self.tokens.append(each_token)

            self.kws.subscribe(self.tokens)
            self.kws.set_mode(self.kws.MODE_FULL,self.tokens)
            logger.info(f"Subscribing to new tokens. The tokens are: {self.tokens}")

    def unsubscribe_tokens(self, tokens_list):
        if type(tokens_list) == list and len(tokens_list) > 0:
            for each_token in tokens_list:
                if each_token in self.tokens:
                    self.tokens.remove(each_token)

            self.kws.unsubscribe(tokens_list)
            logger.info(f"Unsubscribing from tokens: {tokens_list}")
        