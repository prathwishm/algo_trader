import time
from convert_float_to_tick_price import convert_to_tick_price
from telegram_bot import telegram_bot_sendtext
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('orders.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(file_handler)

class Class_Orders:
    def __init__(self, kite, redis_obj, kite_functions):
        self.kite = kite
        self.order_id_dict = {}
        self.redis = redis_obj
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
            
            token = self.kite_functions.get_symbol_token(symbol)

            depth = eval(self.redis.get(str(token)+'_depth'))

            # IF websocket is working use market depth to place limit order. Else place market order.
            if type(depth) == dict:

                if buy_sell == "buy":
                    price = convert_to_tick_price(depth['sell'][1]['price'] + (0.02 * depth['sell'][1]['price']) )
                        
                elif buy_sell == "sell":
                    price = convert_to_tick_price(depth['buy'][1]['price'] - (0.02 * depth['buy'][1]['price']) )
                
                placed_order_id = kite.place_order(tradingsymbol=symbol,
                                            exchange=kite.EXCHANGE_NFO,
                                            transaction_type=t_type,
                                            quantity=quantity,
                                            order_type=kite.ORDER_TYPE_LIMIT,
                                            price=price,
                                            product=kite.PRODUCT_MIS,
                                            variety=kite.VARIETY_REGULAR)
            else:
                print(f'Placing market order for {symbol}')
                placed_order_id = kite.place_order(tradingsymbol=symbol,
                                            exchange=kite.EXCHANGE_NFO,
                                            transaction_type=t_type,
                                            quantity=quantity,
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            product=kite.PRODUCT_MIS,
                                            variety=kite.VARIETY_REGULAR)
            telegram_bot_sendtext(f'Placed {quantity} quantity {buy_sell} order for {symbol}')
            return placed_order_id

        except Exception as e:
            logger.exception(f"Error while placing market order for {symbol}. Error: "+ str(e))
            telegram_bot_sendtext(f'Error while placing {quantity} quantity {buy_sell} order for {symbol}. Error: '+str(e))
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
            telegram_bot_sendtext(f'Placed {quantity} quantity {buy_sell} STOPLOSS order for {symbol}. Trigger price is {trigger_price}')
            return sl_order_id
        except Exception as e:
            logger.exception(f"Error while placing SL order for {symbol}. Error: "+ str(e))
            telegram_bot_sendtext(f'Error while placing {quantity} quantity {buy_sell} STOPLOSS order for {symbol}. Trigger price is {trigger_price}. Error: '+str(e))
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
            logger.exception(f"Error while placing SL order for {symbol}. Error: "+ str(e))
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
            logger.exception(f"Error while Modifying SL order for {order_id}. Error: "+ str(e))
            return -1

    def cancel_order(self, order_id):
        try:
            kite = self.kite

            returned_order_id = kite.cancel_order(variety = kite.VARIETY_REGULAR, order_id = order_id)

            return returned_order_id
        except Exception as e:
            logger.exception(f"Error while Cancelling order for {order_id}. Error: "+ str(e))
            return -1

    def exit_position(self, symbol, buy_sell, quantity):
        # Exit position at best bid/offer
        try:
            kite = self.kite
            if 'NSE:' in symbol:
                symbol = symbol[4:]

            token = self.kite_functions.get_symbol_token(symbol)

            depth  = eval(self.redis.get(str(token)+'_depth'))

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
            logger.exception(f"Error while Exiting from {symbol}. Error: "+ str(e))
            return -1