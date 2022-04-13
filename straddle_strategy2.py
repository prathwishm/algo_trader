import datetime
import pytz
import pandas as pd
import traceback
import time
from convert_float_to_tick_price import convert_to_tick_price
from telegram_bot import telegram_bot_sendtext

def get_nifty_atm_strike(ltp):
    diff = ltp % 50
    if diff > 25:
        atm_strike = ltp - diff +50
    else:
        atm_strike = ltp - diff
    return atm_strike

def get_banknifty_atm_strike(ltp):
    diff = ltp % 100
    if diff > 50:
        atm_strike = ltp - diff + 100
    else:
        atm_strike = ltp - diff
    return atm_strike

class straddles:
    def __init__(self, kite, kite_func, orders_obj, redis_obj, ticker, margin):
        self.kite = kite
        self.kite_functions = kite_func
        self.max_trade_margin = margin
        self.orders_obj = orders_obj
        self.redis = redis_obj
        self.ticker = ticker
        self.placed_bnf_9_20_straddle = False
        self.placed_nf_10_45_straddle = False
        self.placed_bnf_11_45_straddle = False
        self.sl_order_id_list = []
        self.traded_symbols_list = []
        self.exit_procedure_done = False
        self.nf_bnf_option_tokens = []
        self.watchlist = {}

        self.nifty_token = kite_func.get_symbol_token('NSE:NIFTY 50')
        self.bank_nifty_token = kite_func.get_symbol_token('NSE:NIFTY BANK')
        self.nf_bnf_option_tokens.extend([self.nifty_token, self.bank_nifty_token])
        self.bnf_920_dict = {}
        self.bnf_11_45_dict = {}
        self.exit_2_55_done = False
        self.exit_3_00_done = False

        # nifty_ltp = kite.ltp('NSE:NIFTY 50')['NSE:NIFTY 50']['last_price']
        # nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
        # banknifty_ltp = kite.ltp('NSE:NIFTY BANK')['NSE:NIFTY BANK']['last_price']
        # bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
        # nf_strike = nf_atm_strike
        # bnf_strike = bnf_atm_strike
        # for i in range(10):
        #     symbol_ce, nf_token_ce = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'CE')
        #     symbol_pe, nf_token_pe = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'PE')
        #     symbol_ce, bnf_token_ce = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'CE')
        #     symbol_pe, bnf_token_pe = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'PE')
        #     self.nf_bnf_option_tokens.extend([nf_token_ce, nf_token_pe, bnf_token_ce, bnf_token_pe])
        #     nf_strike += 50
        #     bnf_strike += 100
        # nf_strike = nf_atm_strike
        # bnf_strike = bnf_atm_strike
        # for i in range(10):
        #     nf_strike -= 50
        #     bnf_strike -= 100
        #     symbol_ce, nf_token_ce = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'CE')
        #     symbol_pe, nf_token_pe = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'PE')
        #     symbol_ce, bnf_token_ce = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'CE')
        #     symbol_pe, bnf_token_pe = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'PE')
        #     self.nf_bnf_option_tokens.extend([nf_token_ce, nf_token_pe, bnf_token_ce, bnf_token_pe])
        # #print(self.nf_bnf_option_tokens)

    def short_bnf_straddle(self, qty, sl_type):
        try:
            #banknifty_ltp = self.kite.ltp('NSE:NIFTY BANK')['NSE:NIFTY BANK']['last_price']
            banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
            #banknifty_ltp = self.ticker.ltp_dict[self.bank_nifty_token]
            bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            bnf_symbol_ce, bnf_token_ce = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike, 'CE')
            bnf_symbol_pe, bnf_token_pe = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike, 'PE')
            ce_order_id = self.orders_obj.place_market_order(symbol = bnf_symbol_ce, buy_sell= "sell", quantity=qty)
            pe_order_id = self.orders_obj.place_market_order(symbol = bnf_symbol_pe, buy_sell= "sell", quantity=qty)
            self.traded_symbols_list.extend([bnf_symbol_ce, bnf_symbol_pe])
            time.sleep(2)

            for each_order in self.kite.orders():
                if each_order['order_id'] == ce_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        if sl_type == 'point_based':
                            trigger_price_bnf = avg_sell_price + 40
                        elif sl_type == 'percent_based':
                            trigger_price_bnf = convert_to_tick_price(avg_sell_price + (avg_sell_price * .2))
                        print("Placing CE Sl order for BNF at", trigger_price_bnf)
                        ce_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=bnf_symbol_ce, buy_sell="buy", trigger_price= trigger_price_bnf, price = trigger_price_bnf +40, quantity=qty)
                        if ce_sl_order_id!= -1:
                            self.sl_order_id_list.append(ce_sl_order_id)
                        else:
                            print("BNF straddle CE option Stop Loss order is not Placed!!!!!")
                    else:
                        print("BNF straddle CE option sell order is not filled!!!!!")

                if each_order['order_id'] == pe_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        if sl_type == 'point_based':
                            trigger_price_bnf = avg_sell_price + 40
                        elif sl_type == 'percent_based':
                            trigger_price_bnf = convert_to_tick_price(avg_sell_price + (avg_sell_price * .2))
                        print("Placing PE Sl order for BNF at", trigger_price_bnf)
                        pe_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=bnf_symbol_pe, buy_sell="buy", trigger_price= trigger_price_bnf, price = trigger_price_bnf +40, quantity=qty)
                        if pe_sl_order_id!= -1:
                            self.sl_order_id_list.append(pe_sl_order_id)
                        else:
                            print("9:45 straddle PE option Stop Loss order is not Placed!!!!!")
                    else:
                        print("9:45 straddle PE option sell order is not filled!!!!!")
        except Exception as e:
            print("Unexpected error while shorting bnf straddle. Error: "+str(e))
            traceback.print_exc()

    def short_nifty_straddle(self, qty):
        try:
            #nifty_ltp = self.kite.ltp('NSE:NIFTY 50')['NSE:NIFTY 50']['last_price']
            nifty_ltp = eval(self.redis.get(str(self.nifty_token)))
            #nifty_ltp = self.ticker.ltp_dict[self.nifty_token]
            nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
            self.add_straddle_to_websocket(nf_atm_strike, index = 'NIFTY')
            nf_symbol_ce, nf_token_ce = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike, 'CE')
            nf_symbol_pe, nf_token_pe = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike, 'PE')
            ce_order_id = self.orders_obj.place_market_order(symbol = nf_symbol_ce, buy_sell= "sell", quantity=qty)
            pe_order_id = self.orders_obj.place_market_order(symbol = nf_symbol_pe, buy_sell= "sell", quantity=qty)
            self.traded_symbols_list.extend([nf_symbol_ce, nf_symbol_pe])
            time.sleep(2)

            for each_order in self.kite.orders():
                if each_order['order_id'] == ce_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        trigger_price_nf = convert_to_tick_price(avg_sell_price + (avg_sell_price * .4))
                        print("Placing CE Sl order for NF at", trigger_price_nf)

                        ce_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=nf_symbol_ce, buy_sell="buy", trigger_price= trigger_price_nf, price = trigger_price_nf + 20, quantity=qty)
                        if ce_sl_order_id!= -1:
                            self.sl_order_id_list.append(ce_sl_order_id)
                        else:
                            telegram_bot_sendtext("NIFTY straddle CE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext("NIFTY straddle CE option sell order is not filled!!!!!")

                if each_order['order_id'] == pe_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        trigger_price_nf = convert_to_tick_price(avg_sell_price + (avg_sell_price * .4))
                        print("Placing PE Sl order for NF at", trigger_price_nf)
                        pe_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=nf_symbol_pe, buy_sell="buy", trigger_price= trigger_price_nf, price = trigger_price_nf + 20, quantity=qty)
                        if pe_sl_order_id!= -1:
                            self.sl_order_id_list.append(pe_sl_order_id)
                        else:
                            telegram_bot_sendtext("NIFTY straddle PE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext("NIFTY straddle PE option sell order is not filled!!!!!")
        except Exception as e:
            print("Unexpected error while shorting bnf straddle. Error: "+str(e))
            telegram_bot_sendtext("Unexpected error while shorting bnf straddle. Error: "+str(e))
            traceback.print_exc()

    
    def main(self):
        current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))

        if current_dt.hour < 14 or (current_dt.hour == 14 and current_dt.minute < 40):
            self.short_options_on_trigger()

        if not self.placed_bnf_9_20_straddle and current_dt.hour == 9 and (current_dt.minute >=20 or (current_dt.minute >=19 and current_dt.second >=54)):
            self.placed_bnf_9_20_straddle = True
            #self.short_bnf_straddle(25, 'percent_based')
            self.add_bnf_straddle_to_watchlist('9_20_straddle',25)

        if not self.placed_nf_10_45_straddle and current_dt.hour == 10 and (current_dt.minute >=45 or (current_dt.minute >=44 and current_dt.second >=54)):
            self.placed_nf_10_45_straddle = True
            self.short_nifty_straddle(50)

        if not self.placed_bnf_11_45_straddle and current_dt.hour == 11 and (current_dt.minute >=45 or (current_dt.minute >=44 and current_dt.second >=54)):
            self.placed_bnf_11_45_straddle = True
            #self.short_bnf_straddle(25, 'percent_based')
            self.add_bnf_straddle_to_watchlist('11_45_straddle', 25)

        if not self.exit_2_55_done and current_dt.hour == 14 and (current_dt.minute >=55 or (current_dt.minute >=54 and current_dt.second >=54)):
            self.exit_2_55_done = True
            self.cancel_orders_and_exit_position(self.bnf_920_dict, 25)

        if not self.exit_3_00_done and current_dt.hour == 15 and current_dt.minute >=0 and current_dt.second >=4:
            self.exit_3_00_done = True
            self.cancel_orders_and_exit_position(self.bnf_11_45_dict, 25)

        
        if not self.exit_procedure_done and current_dt.hour == 15 and (current_dt.minute >=10 or (current_dt.minute >=9 and current_dt.second >=54)):
            self.exit_procedure_done = True
            for each_order in self.kite.orders():
                if each_order['order_id'] in self.sl_order_id_list:
                    if each_order['status'] == 'TRIGGER PENDING':
                        self.orders_obj.cancel_order(each_order['order_id'])

            for each_pos in self.kite.positions()['day']:
                if each_pos['tradingsymbol'] in self.traded_symbols_list and each_pos['product'] == 'MIS' and each_pos['quantity'] != 0:
                    exit_quantity = abs(each_pos['quantity'])
                    exit_type = "sell" if each_pos['quantity'] > 0 else "buy"
                    if exit_quantity > 0:
                        self.orders_obj.place_market_order(symbol = each_pos['tradingsymbol'], buy_sell= exit_type, quantity=exit_quantity)

    def cancel_orders_and_exit_position(self, symbols_dict, qty):
        for each_order in self.kite.orders():
            if each_order['order_id'] in symbols_dict.values():
                if each_order['status'] == 'TRIGGER PENDING':
                    self.orders_obj.cancel_order(each_order['order_id'])

        for each_pos in self.kite.positions()['day']:
            if each_pos['tradingsymbol'] in symbols_dict.keys() and each_pos['product'] == 'MIS' and each_pos['quantity'] != 0:
                exit_quantity = qty
                exit_type = "sell" if each_pos['quantity'] > 0 else "buy"
                if exit_quantity > 0:
                    self.orders_obj.place_market_order(symbol = each_pos['tradingsymbol'], buy_sell= exit_type, quantity=exit_quantity)




    def add_straddle_to_websocket(self, atm_strike, index = 'BANKNIFTY'):
        if index == 'BANKNIFTY':
            strike_list = [atm_strike - 100, atm_strike, atm_strike+ 100]
        elif index == 'NIFTY':
            strike_list = [atm_strike - 50, atm_strike, atm_strike+ 50]

        tokens_list = []
        for each_strike in strike_list:
            symbol_ce, token_ce = self.kite_functions.get_options_symbol_and_token(index, each_strike, 'CE')
            symbol_pe, token_pe = self.kite_functions.get_options_symbol_and_token(index, each_strike, 'PE')
            if token_pe not in self.nf_bnf_option_tokens:
                tokens_list.extend([token_ce, token_pe])
                self.nf_bnf_option_tokens.extend([token_ce, token_pe])

        if len(tokens_list) > 0:
            telegram_bot_sendtext(f'ADDING {tokens_list} to websocket')
            self.ticker.subscribe_tokens(tokens_list)
            time.sleep(5)


    def add_bnf_straddle_to_watchlist(self, strategy, qty):
        try:
            #banknifty_ltp = self.kite.ltp('NSE:NIFTY BANK')['NSE:NIFTY BANK']['last_price']
            banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
            #banknifty_ltp = self.ticker.ltp_dict[self.bank_nifty_token]
            bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            self.add_straddle_to_websocket(bnf_atm_strike, index = 'BANKNIFTY')
            banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
            #banknifty_ltp = self.ticker.ltp_dict[self.bank_nifty_token]
            bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            bnf_symbol_ce, bnf_token_ce = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike, 'CE')
            bnf_symbol_pe, bnf_token_pe = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike, 'PE')

            #ltp_ce = self.ticker.ticker_dict[bnf_token_ce][-1][1]
            ltp_ce = eval(self.redis.get(str(bnf_token_ce)))
            #ltp_ce = self.ticker.ltp_dict[bnf_token_ce]
            ce_trigger_price = convert_to_tick_price(ltp_ce + (ltp_ce * .2))
            #ltp_pe = self.ticker.ticker_dict[bnf_token_pe][-1][1]
            ltp_pe = eval(self.redis.get(str(bnf_token_pe)))
            #ltp_pe = self.ticker.ltp_dict[bnf_token_pe]
            pe_trigger_price = convert_to_tick_price(ltp_pe + (ltp_pe * .2))
            self.watchlist[strategy + 'ce'] = {'token': bnf_token_ce,'symbol': bnf_symbol_ce,'price': ltp_ce, 'trigger_price': ce_trigger_price,
                                            'datetime': datetime.datetime.now(), 'opposite_key':strategy + 'pe', 'quantity':qty}
            self.watchlist[strategy + 'pe'] = {'token': bnf_token_pe,'symbol': bnf_symbol_pe,'price': ltp_pe, 'trigger_price': pe_trigger_price,
                                            'datetime': datetime.datetime.now(), 'opposite_key':strategy + 'ce', 'quantity':qty}

        except Exception as e:
            print("Unexpected error in add_bnf_straddle_to_watchlist. Error: "+str(e))
            telegram_bot_sendtext("Unexpected error in add_bnf_straddle_to_watchlist. Error: "+str(e))
            traceback.print_exc()

    def short_options_on_trigger(self):
        list_of_tokens_to_pop_from_watchlist = []
        for strategy_option, values_dict in self.watchlist.items():
            if strategy_option in list_of_tokens_to_pop_from_watchlist:
                continue
            ltp_data = list(map(eval, self.redis.lrange(str(values_dict['token'])+'_data', -25, -1)))
            #ltp_data = self.ticker.ticker_dict[values_dict['token']][-25:]
            #for tick_list in self.ticker.ticker_dict[strategy_option][-50:]: #last 50 values are used as 5 second data is not expected to exceed 50 ticks
            for tick_list in ltp_data:
                if tick_list[1] > values_dict['trigger_price'] and tick_list[0] > values_dict['datetime']:
                    #self.watchlist.pop(strategy_option)
                    list_of_tokens_to_pop_from_watchlist.append(strategy_option)
                    opposite_key = values_dict['opposite_key']
                    list_of_tokens_to_pop_from_watchlist.append(opposite_key)
                    symbol = self.watchlist[opposite_key]['symbol']
                    sl_price = self.watchlist[opposite_key]['trigger_price']
                    # if '9' in strategy_option:
                    #     sl_price = min(self.watchlist[opposite_key]['trigger_price'], tick_list[1]+80)
                    # else:
                    #     sl_price = min(self.watchlist[opposite_key]['trigger_price'], tick_list[1]+120)
                    qty = self.watchlist[opposite_key]['quantity']
                    self.short_option_and_place_sl(symbol=symbol, sl_price=sl_price, qty=qty, dt = values_dict['datetime'])

                    #self.watchlist.pop(opposite_key)
                    #list_of_tokens_to_pop_from_watchlist.append(opposite_key)
                    #place orders
                    
                    break

        for strat_option in list_of_tokens_to_pop_from_watchlist:
            try:
                self.watchlist.pop(strat_option)
            except Exception as e:
                print(f"Unexpected error while popping {strat_option} from watchlist. Error: "+str(e))
                telegram_bot_sendtext(f"Unexpected error while popping {strat_option} from watchlist. Error: "+str(e))
                traceback.print_exc()

    

    def short_option_and_place_sl(self, symbol, sl_price, qty, dt):
            order_id = self.orders_obj.place_market_order(symbol = symbol, buy_sell= "sell", quantity=qty)
            self.traded_symbols_list.append(symbol)
            strategy_entry_hour = None
            sl_points = 120
            if dt.hour == 9:
                self.bnf_920_dict[symbol] = None
                strategy_entry_hour = 9
                sl_points = 80
            elif dt.hour == 11:
                self.bnf_11_45_dict[symbol] = None
                strategy_entry_hour = 11
            time.sleep(1)
            sl_order_is_placed = False
            for _ in range(5):
                if sl_order_is_placed:
                    break
                time.sleep(1)
                for each_order in self.kite.orders():
                    if each_order['order_id'] == order_id:
                        if each_order['status'] == 'COMPLETE':
                            avg_sell_price = each_order['average_price']
                            sl_price = min(sl_price, avg_sell_price+sl_points)
                            telegram_bot_sendtext(f"Placing Sl order for {symbol} at {sl_price}")

                            sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=symbol, buy_sell="buy", trigger_price= sl_price, price = sl_price + 20, quantity=qty)
                            if sl_order_id!= -1:
                                sl_order_is_placed = True
                                self.sl_order_id_list.append(sl_order_id)
                                if strategy_entry_hour == 9:
                                    self.bnf_920_dict[symbol] = sl_order_id
                                elif strategy_entry_hour == 11:
                                    self.bnf_11_45_dict[symbol] = sl_order_id
                            else:
                                print(f"Sl order for {symbol} at {sl_price} is not Placed!!!!!")
                        else:
                            print(f"{symbol} option sell order is not filled!!!!!")

            if not sl_order_is_placed:
                telegram_bot_sendtext(f"{symbol} option sell order is not filled!!!!!")