import datetime
import pandas as pd
import traceback
import time
from convert_float_to_tick_price import convert_to_tick_price

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
    def __init__(self, kite, kite_func, orders_obj, margin):
        self.kite = kite
        self.kite_functions = kite_func
        self.max_trade_margin = margin
        self.orders_obj = orders_obj
        self.placed_bnf_9_45_straddle = False
        self.placed_nf_10_45_straddle = False
        self.placed_bnf_11_15_straddle = False
        self.sl_order_id_list = []
        self.traded_symbols_list = []
        self.exit_procedure_done = False
        self.nf_bnf_option_tokens = []
        nifty_ltp = kite.ltp('NSE:NIFTY 50')['NSE:NIFTY 50']['last_price']
        nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
        banknifty_ltp = kite.ltp('NSE:NIFTY BANK')['NSE:NIFTY BANK']['last_price']
        bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
        nf_strike = nf_atm_strike
        bnf_strike = bnf_atm_strike
        for i in range(20):
            symbol_ce, nf_token_ce = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'CE')
            symbol_pe, nf_token_pe = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'PE')
            symbol_ce, bnf_token_ce = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'CE')
            symbol_pe, bnf_token_pe = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'PE')
            self.nf_bnf_option_tokens.extend([nf_token_ce, nf_token_pe, bnf_token_ce, bnf_token_pe])
            nf_strike += 50
            bnf_strike += 100
        nf_strike = nf_atm_strike
        bnf_strike = bnf_atm_strike
        for i in range(20):
            nf_strike -= 50
            bnf_strike -= 100
            symbol_ce, nf_token_ce = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'CE')
            symbol_pe, nf_token_pe = kite_func.get_options_symbol_and_token('NIFTY', nf_strike, 'PE')
            symbol_ce, bnf_token_ce = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'CE')
            symbol_pe, bnf_token_pe = kite_func.get_options_symbol_and_token('BANKNIFTY', bnf_strike, 'PE')
            self.nf_bnf_option_tokens.extend([nf_token_ce, nf_token_pe, bnf_token_ce, bnf_token_pe])
        print(self.nf_bnf_option_tokens)

    def short_bnf_straddle(self, qty, sl_type):
        try:
            banknifty_ltp = self.kite.ltp('NSE:NIFTY BANK')['NSE:NIFTY BANK']['last_price']
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
            nifty_ltp = self.kite.ltp('NSE:NIFTY 50')['NSE:NIFTY 50']['last_price']
            nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
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
                        print("Placing CE Sl order for BNF at", trigger_price_nf)

                        ce_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=nf_symbol_ce, buy_sell="buy", trigger_price= trigger_price_nf, price = trigger_price_nf + 20, quantity=qty)
                        if ce_sl_order_id!= -1:
                            self.sl_order_id_list.append(ce_sl_order_id)
                        else:
                            print("NIFTY straddle CE option Stop Loss order is not Placed!!!!!")
                    else:
                        print("NIFTY straddle CE option sell order is not filled!!!!!")

                if each_order['order_id'] == pe_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        trigger_price_nf = convert_to_tick_price(avg_sell_price + (avg_sell_price * .4))
                        print("Placing PE Sl order for BNF at", trigger_price_nf)
                        pe_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=nf_symbol_pe, buy_sell="buy", trigger_price= trigger_price_nf, price = trigger_price_nf + 20, quantity=qty)
                        if pe_sl_order_id!= -1:
                            self.sl_order_id_list.append(pe_sl_order_id)
                        else:
                            print("NIFTY straddle PE option Stop Loss order is not Placed!!!!!")
                    else:
                        print("NIFTY straddle PE option sell order is not filled!!!!!")
        except Exception as e:
            print("Unexpected error while shorting bnf straddle. Error: "+str(e))
            traceback.print_exc()

    
    def main(self):
        current_dt = datetime.datetime.now()

        if not self.placed_bnf_9_45_straddle and current_dt.hour == 9 and current_dt.minute >=45:
            self.placed_bnf_9_45_straddle = True
            self.short_bnf_straddle(25, 'point_based')

        if not self.placed_nf_10_45_straddle and current_dt.hour == 10 and current_dt.minute >=45:
            self.placed_nf_10_45_straddle = True
            self.short_nifty_straddle(50)

        if not self.placed_bnf_11_15_straddle and current_dt.hour == 11 and current_dt.minute >=15:
            self.placed_bnf_11_15_straddle = True
            self.short_bnf_straddle(25, 'percent_based')
        
        if not self.exit_procedure_done and current_dt.hour == 15 and current_dt.minute >=10:
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

            


            