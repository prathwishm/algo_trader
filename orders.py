import time
from math import modf
from convert_float_to_tick_price import convert_to_tick_price

class Class_Orders:
    def __init__(self, kite, ticker, kite_functions):
        self.kite = kite
        self.order_id_dict = {}
        self.ticker = ticker
        self.kite_functions = kite_functions

    def place_market_order(self, symbol, buy_sell, quantity):
        try:
            kite = self.kite
            if 'NSE:' in symbol or 'NFO:' in symbol:
                symbol = symbol[4:]
            
            if buy_sell == "buy":
                t_type=kite.TRANSACTION_TYPE_BUY
                    
            elif buy_sell == "sell":
                t_type=kite.TRANSACTION_TYPE_SELL

            
            placed_order_id = kite.place_order(tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=t_type,
                                        quantity=quantity,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        product=kite.PRODUCT_MIS,
                                        variety=kite.VARIETY_REGULAR)

            return placed_order_id

        except Exception as e:
            print(f"Error while placing market order for {symbol}. Error: "+ str(e))
            return -1

    def place_sl_order_for_options(self, symbol, buy_sell, trigger_price, price, quantity):
        # Place long/short stoploss order
        try:
            kite = self.kite

            if 'NSE:' in symbol or 'NFO:' in symbol:
                symbol = symbol[4:]
            
            if buy_sell == "buy":
                t_type=kite.TRANSACTION_TYPE_BUY
                    
            elif buy_sell == "sell":
                t_type=kite.TRANSACTION_TYPE_SELL

            sl_order_id = kite.place_order(tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=t_type,
                                        quantity=quantity,
                                        order_type=kite.ORDER_TYPE_SL,
                                        price=price,
                                        trigger_price = trigger_price,
                                        product=kite.PRODUCT_MIS,
                                        variety=kite.VARIETY_REGULAR)

            return sl_order_id
        except Exception as e:
            print(f"Error while placing SL order for {symbol}. Error: "+ str(e))
            return -1

    def enter_position(self, symbol, buy_sell, quantity, strategy=None):
        # Place long/short market order along with SL and target order
        try:
            kite = self.kite
            if 'NSE:' in symbol or 'NFO:' in symbol:
                symbol = symbol[4:]

            token = self.kite_functions.get_symbol_token(symbol)
            depth  = self.ticker.depth_dict[token]
            
            if buy_sell == "buy":
                t_type=kite.TRANSACTION_TYPE_BUY
                price = depth['sell'][0]['price']
                sl_order_type = "sell"
                sl_price = price - 40
                    
            elif buy_sell == "sell":
                t_type=kite.TRANSACTION_TYPE_SELL
                price = depth['buy'][0]['price']
                sl_order_type = "buy"
                sl_price = price + 40

            
            placed_order_id = kite.place_order(tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=t_type,
                                        quantity=quantity,
                                        order_type=kite.ORDER_TYPE_LIMIT,
                                        price=price,
                                        product=kite.PRODUCT_MIS,
                                        variety=kite.VARIETY_REGULAR)

            self.order_id_dict.update({placed_order_id: {'strategy': strategy ,'order_type': buy_sell, 'tradingsymbol':symbol, 'price': price,
                                        'time': time.time(), 'sl_id':None, 'target_id':None, 'quantity':quantity, 'sl_price': sl_price,
                                        'sl_order_placed': False, 'sl_order_type': sl_order_type, 'filled_qty': 0}})


            return placed_order_id

        except Exception as e:
            print(f"Error while placing Entry order for {symbol}. Error: "+ str(e))
            return -1

    def place_order(self, symbol, buy_sell, trigger_price, price, quantity, sl_price, strategy=None):
        # Place long/short order along with SL and target order
        try:
            kite = self.kite
            if 'NSE:' in symbol:
                symbol = symbol[4:]

            token = self.kite_functions.get_symbol_token(symbol)
            ltp = self.ticker.ticker_dict[token][-1][-2]
            depth  = self.ticker.depth_dict[token]

            place_limit_order = False
            
            if buy_sell == "buy":
                t_type=kite.TRANSACTION_TYPE_BUY
                sl_order_type = "sell"
                if ltp >= trigger_price:
                    place_limit_order = True
                    if depth['sell'][0]['price'] < price:
                        price = depth['sell'][0]['price']
                elif price < trigger_price:
                    trigger_price = convert_to_tick_price(price - (0.001 * price) )
                    
            elif buy_sell == "sell":
                t_type=kite.TRANSACTION_TYPE_SELL
                sl_order_type = "buy"
                if ltp <= trigger_price:
                    place_limit_order = True
                    if depth['buy'][0]['price'] > price:
                        price = depth['buy'][0]['price']
                elif price > trigger_price:
                    trigger_price = convert_to_tick_price(price + (0.001 * price) )

            
            if place_limit_order:
                placed_order_id = kite.place_order(tradingsymbol=symbol,
                                            exchange=kite.EXCHANGE_NSE,
                                            transaction_type=t_type,
                                            quantity=quantity,
                                            order_type=kite.ORDER_TYPE_LIMIT,
                                            price=price,
                                            product=kite.PRODUCT_MIS,
                                            variety=kite.VARIETY_REGULAR)
            else:
                placed_order_id = kite.place_order(tradingsymbol=symbol,
                                            exchange=kite.EXCHANGE_NSE,
                                            transaction_type=t_type,
                                            quantity=quantity,
                                            order_type=kite.ORDER_TYPE_SL,
                                            price=price,
                                            trigger_price = trigger_price,
                                            product=kite.PRODUCT_MIS,
                                            variety=kite.VARIETY_REGULAR)


            self.order_id_dict.update({placed_order_id: {'strategy': strategy ,'order_type': buy_sell, 'tradingsymbol':symbol, 'price': price,
                                        'time': time.time(), 'sl_id':None, 'target_id':None, 'quantity':quantity, 'sl_price': sl_price,
                                        'sl_order_placed': False, 'sl_order_type': sl_order_type, 'filled_qty': 0}})

            return placed_order_id
        
        except Exception as e:
            print(f"Error while placing Entry order for {symbol}. Error: "+ str(e))
            return -1

    def place_sl_order(self, symbol, buy_sell, trigger_price, quantity):
        # Place long/short stoploss order
        try:
            kite = self.kite

            if 'NSE:' in symbol:
                symbol = symbol[4:]
            
            if buy_sell == "buy":
                t_type=kite.TRANSACTION_TYPE_BUY
                price = convert_to_tick_price(trigger_price + (0.001 * trigger_price) )
                    
            elif buy_sell == "sell":
                t_type=kite.TRANSACTION_TYPE_SELL
                price = convert_to_tick_price(trigger_price - (0.001 * trigger_price) )

            sl_order_id = kite.place_order(tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NSE,
                                        transaction_type=t_type,
                                        quantity=quantity,
                                        order_type=kite.ORDER_TYPE_SL,
                                        price=price,
                                        trigger_price = trigger_price,
                                        product=kite.PRODUCT_MIS,
                                        variety=kite.VARIETY_REGULAR)

            return sl_order_id
        except Exception as e:
            print(f"Error while placing SL order for {symbol}. Error: "+ str(e))
            return -1

    def modify_sl_order(self, order_id, quantity=None, price=None, trigger_price= None):
        # Modify SL ORDER
        try:
            kite = self.kite

            sl_order_id = kite.modify_order(variety = kite.VARIETY_REGULAR, order_id= order_id,
                                            quantity = quantity, order_type = kite.ORDER_TYPE_SL,
                                            price=price, trigger_price= trigger_price)

            return sl_order_id
        except Exception as e:
            print(f"Error while Modifying SL order for {order_id}. Error: "+ str(e))
            return -1

    def cancel_order(self, order_id):
        try:
            kite = self.kite

            returned_order_id = kite.cancel_order(variety = kite.VARIETY_REGULAR, order_id = order_id)

            return returned_order_id
        except Exception as e:
            print(f"Error while Cancelling order for {order_id}. Error: "+ str(e))
            return -1

    def exit_position(self, symbol, buy_sell, quantity):
        # Exit position at best bid/offer
        try:
            kite = self.kite
            if 'NSE:' in symbol:
                symbol = symbol[4:]

            token = self.kite_functions.get_symbol_token(symbol)
            depth  = self.ticker.depth_dict[token]

            
            if buy_sell == "buy":
                t_type=kite.TRANSACTION_TYPE_BUY
                price = depth['sell'][0]['price']
                    
            elif buy_sell == "sell":
                t_type=kite.TRANSACTION_TYPE_SELL
                price = depth['buy'][0]['price']

            
            placed_order_id = kite.place_order(tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NSE,
                                        transaction_type=t_type,
                                        quantity=quantity,
                                        order_type=kite.ORDER_TYPE_LIMIT,
                                        price=price,
                                        product=kite.PRODUCT_MIS,
                                        variety=kite.VARIETY_REGULAR)


            return placed_order_id
        
        except Exception as e:
            print(f"Error while Exiting from {symbol}. Error: "+ str(e))
            return -1