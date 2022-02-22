import datetime

class Ticker_class():
    """
    Class to consume tick by tick data.
    Stores the latest price and volume in ticker_dict.
    Stores the latest depth in depth_dict.
    The key for ticker_dict and depth_dict are instrument token.

    microsecond is added to "last_trade_time" to ensure that mutiple ticks
    having same timestamp are handled.

    latest tick data is compared with last stored tick data of that instrument to prevent duplicate ticks
    """
    
    def __init__(self, kite, tokens):
        self.kite = kite
        self.tokens = tokens
        self.ticker_dict = {}
        self.depth_dict = {}
        self.subscribe_list = []
        self.subscribe_new_tokens = False
        self.unsubscribe_list = []
        self.unsubscribe_from_token = False
        self.stop_ticker = False
        self.counter = 1


    def start_ticker(self):
        if len(self.tokens) == 0:
            print("No Tokens found for ticker service")
            return None

        for each_token in self.tokens:
            self.ticker_dict[each_token] = []
            self.depth_dict[each_token] = {}
 
        def on_ticks(ws,ticks):
            for tick in ticks:
                ticker_token = tick['instrument_token']

                try:
                    if not (self.ticker_dict[ticker_token][-1][-1] == tick['volume'] and self.ticker_dict[ticker_token][-1][-2] == tick['last_price']):
                        ts = tick['timestamp'] + datetime.timedelta(microseconds=self.counter)
                        vals = [ts, tick['last_price'], tick['volume']]
                        self.ticker_dict[ticker_token].append(vals)
                        self.depth_dict[ticker_token] = tick['depth']

                except IndexError:
                    print(ticker_token, "not in dict.")
                    if (tick['timestamp'].hour >= 9 and tick['timestamp'].minute >= 15) or tick['timestamp'].hour >= 10:
                        ts = tick['timestamp'] + datetime.timedelta(microseconds=self.counter)
                        vals = [ts, tick['last_price'], tick['volume']]
                        self.ticker_dict[ticker_token].append(vals)

                except KeyError as key:
                    print("Unexpected  KeyError in ticker")
                    self.ticker_dict[ticker_token] = []

                except Exception as e:
                    print("Unexpected error in ticker. Error: "+str(e))

                self.counter +=1
                if self.counter >= 999998:
                    self.counter = 1

            # Subscribe to new Tokens dynamically
            if self.subscribe_new_tokens:
                self.subscribe_new_tokens = True
                if len(self.subscribe_list) > 0:
                    ws.subscribe(self.subscribe_list)
                    ws.set_mode(ws.MODE_FULL,self.subscribe_list)
                    ticker_dict_keys = list(self.ticker_dict.keys())
                    for each_token in self.subscribe_list:
                        if each_token not in ticker_dict_keys:
                            self.ticker_dict[each_token] = []
                            self.depth_dict[each_token] = {}
                self.subscribe_list = []
                

            # Unsubscribe from Tokens dynamically
            if self.unsubscribe_from_token:
                self.unsubscribe_from_token = False
                if len(self.unsubscribe_list) > 0:
                    ws.unsubscribe(self.unsubscribe_list)
                    self.unsubscribe_list = []

            if self.stop_ticker:
                print("Stopping ticker")
                kws.close()

        def on_connect(ws,response):
            ws.subscribe(self.tokens)
            ws.set_mode(ws.MODE_FULL,self.tokens)

        def on_close(ws, code, reason): 
            ws.stop()

        kws = self.kite.ticker()

        kws.on_ticks = on_ticks
        kws.on_connect = on_connect
        kws.on_close = on_close
        kws.connect(threaded=True)