import datetime
import pytz
#import pandas as pd
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
        self.placed_nf_9_16_strangle = False
        self.placed_bnf_9_20_straddle = False
        self.placed_nf_9_40_strangle = False
        self.placed_bnf_10_05_strangle = False
        self.placed_nf_10_45_straddle = False
        self.placed_bnf_11_15_strangle = False
        self.placed_bnf_11_45_straddle = False
        self.placed_nf_11_30_strangle = False
        self.placed_bnf_13_20_strangle = False
        self.sl_order_id_list = []
        self.traded_symbols_list = []
        self.exit_procedure_done = False
        self.nf_bnf_option_tokens = []
        self.watchlist = {}

        self.nifty_token = kite_func.get_symbol_token('NSE:NIFTY 50')
        self.bank_nifty_token = kite_func.get_symbol_token('NSE:NIFTY BANK')
        self.nf_bnf_option_tokens.extend([self.nifty_token, self.bank_nifty_token])
        self.iso_week_day = datetime.date.today().isoweekday()

        self.nf_9_16_qty = 50
        self.nf_9_16_expiry_qty = 50
        self.bnf_9_20_qty = 25
        self.bnf_10_05_qty  =25
        self.nf_9_40_qty = 50
        self.nf_10_45_qty = 50
        self.bnf_11_15_qty = 25
        self.bnf_11_45_qty = 25
        self.nf_11_30_qty = 50
        self.bnf_13_20_qty = 25

        # if self.iso_week_day == 1:
        #     #Monday
        #     self.bnf_10_05_qty  = 50
        if self.iso_week_day == 2:
            #Tuesday
            self.bnf_11_15_qty  = 50
        if self.iso_week_day == 5:
            #Friday
            self.nf_11_30_qty  = 100
            self.bnf_11_15_qty  = 50

        self.nf_9_16_dict = {}
        self.nf_9_16_expiry_dict = {}
        self.bnf_9_20_dict = {}
        self.bnf_10_05_dict  = {}
        self.nf_9_40_dict = {}
        self.nf_10_45_dict = {}
        self.bnf_11_15_dict = {}
        self.bnf_11_45_dict = {}
        self.nf_11_30_dict = {}
        self.bnf_13_20_dict = {}
        self.exit_12_44_done = False
        self.exit_14_55_done = False
        self.exit_15_00_done = False
        self.exit_15_05_done = False
        self.exit_15_08_done = False
        self.exit_15_10_done = False
        self.exit_15_12_done = False
        self.exit_15_15_done = False
        self.exit_15_17_done = False
        self.exit_15_19_done = False
        self.last_orders_checked_dt = None
        self.buy_hedges_and_increase_quantity = False
        if self.iso_week_day in [3,4]:
            self.buy_hedges_and_increase_quantity = True
            self.last_orders_checked_dt = datetime.datetime.now()
        self.hedges_dict = {}
        self.hedge_exit_sl_order_id_list = []

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

    def short_bnf_straddle(self, qty, sl_percent=0.25, strangle = False, strike_distance = 200):
        try:
            #banknifty_ltp = self.kite.ltp('NSE:NIFTY BANK')['NSE:NIFTY BANK']['last_price']
            banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
            #banknifty_ltp = self.ticker.ltp_dict[self.bank_nifty_token]
            bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            if strangle:
                self.add_itm_strangle_to_websocket(atm_strike = bnf_atm_strike, distance_from_atm = strike_distance, index = 'BANKNIFTY')
                bnf_symbol_ce, bnf_token_ce = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike - strike_distance, 'CE')
                bnf_symbol_pe, bnf_token_pe = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike + strike_distance, 'PE')
            else:
                self.add_straddle_to_websocket(bnf_atm_strike, index = 'BANKNIFTY')
                bnf_symbol_ce, bnf_token_ce = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike, 'CE')
                bnf_symbol_pe, bnf_token_pe = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike, 'PE')

            if self.buy_hedges_and_increase_quantity:
                qty = qty * 3
                hedge_symbol_ce, hedge_token_ce = self.get_hedge_symbol(bnf_symbol_ce)
                hedge_symbol_pe, hedge_token_pe = self.get_hedge_symbol(bnf_symbol_pe)
                hedge_ce_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol_ce, buy_sell= "buy", quantity=qty, use_limit_order = False)
                hedge_pe_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol_pe, buy_sell= "buy", quantity=qty, use_limit_order = False)
                self.traded_symbols_list.extend([hedge_symbol_ce, hedge_symbol_pe])
                time.sleep(1)

            ce_order_id = self.orders_obj.place_market_order(symbol = bnf_symbol_ce, buy_sell= "sell", quantity=qty)
            pe_order_id = self.orders_obj.place_market_order(symbol = bnf_symbol_pe, buy_sell= "sell", quantity=qty)
            self.traded_symbols_list.extend([bnf_symbol_ce, bnf_symbol_pe])
            time.sleep(2)

            current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            for each_order in self.kite.orders():
                if each_order['order_id'] == ce_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        trigger_price_bnf = convert_to_tick_price(avg_sell_price + (avg_sell_price * sl_percent))
                        print("Placing CE Sl order for BNF at", trigger_price_bnf)
                        ce_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=bnf_symbol_ce, buy_sell="buy", trigger_price= trigger_price_bnf, price = trigger_price_bnf +40, quantity=qty)
                        if ce_sl_order_id!= -1:
                            self.sl_order_id_list.append(ce_sl_order_id)
                            if current_dt.hour == 13 and current_dt.minute in [19, 20]:
                                self.bnf_13_20_dict[bnf_symbol_ce] = ce_sl_order_id
                            if self.buy_hedges_and_increase_quantity:
                                self.hedges_dict[ce_sl_order_id] = hedge_symbol_ce
                        else:
                            telegram_bot_sendtext("BNF straddle CE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext("BNF straddle CE option sell order is not filled!!!!!")

                if each_order['order_id'] == pe_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        trigger_price_bnf = convert_to_tick_price(avg_sell_price + (avg_sell_price * sl_percent))
                        print("Placing PE Sl order for BNF at", trigger_price_bnf)
                        pe_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=bnf_symbol_pe, buy_sell="buy", trigger_price= trigger_price_bnf, price = trigger_price_bnf +40, quantity=qty)
                        if pe_sl_order_id!= -1:
                            self.sl_order_id_list.append(pe_sl_order_id)
                            if current_dt.hour == 13 and current_dt.minute in [19, 20]:
                                self.bnf_13_20_dict[bnf_symbol_pe] = pe_sl_order_id
                            if self.buy_hedges_and_increase_quantity:
                                self.hedges_dict[pe_sl_order_id] = hedge_symbol_pe
                        else:
                            telegram_bot_sendtext("BNF straddle PE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext("BNF straddle PE option sell order is not filled!!!!!")
        except Exception as e:
            print("Unexpected error while shorting bnf straddle. Error: "+str(e))
            traceback.print_exc()

    
    def short_nifty_straddle(self, qty, sl_percent=0.4, strangle = False, strike_distance = 100):
        try:
            #nifty_ltp = self.kite.ltp('NSE:NIFTY 50')['NSE:NIFTY 50']['last_price']
            nifty_ltp = eval(self.redis.get(str(self.nifty_token)))
            #nifty_ltp = self.ticker.ltp_dict[self.nifty_token]
            nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
            if strangle:
                self.add_itm_strangle_to_websocket(atm_strike = nf_atm_strike, distance_from_atm = strike_distance, index = 'NIFTY')
                nf_symbol_ce, nf_token_ce = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike - strike_distance, 'CE')
                nf_symbol_pe, nf_token_pe = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike + strike_distance, 'PE')
            else:
                self.add_straddle_to_websocket(nf_atm_strike, index = 'NIFTY')
                nf_symbol_ce, nf_token_ce = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike, 'CE')
                nf_symbol_pe, nf_token_pe = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike, 'PE')
            if self.buy_hedges_and_increase_quantity:
                qty = qty * 3
                hedge_symbol_ce, hedge_token_ce = self.get_hedge_symbol(nf_symbol_ce)
                hedge_symbol_pe, hedge_token_pe = self.get_hedge_symbol(nf_symbol_pe)
                hedge_ce_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol_ce, buy_sell= "buy", quantity=qty, use_limit_order = False)
                hedge_pe_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol_pe, buy_sell= "buy", quantity=qty, use_limit_order = False)
                self.traded_symbols_list.extend([hedge_symbol_ce, hedge_symbol_pe])
                time.sleep(1)

            ce_order_id = self.orders_obj.place_market_order(symbol = nf_symbol_ce, buy_sell= "sell", quantity=qty)
            pe_order_id = self.orders_obj.place_market_order(symbol = nf_symbol_pe, buy_sell= "sell", quantity=qty)
            self.traded_symbols_list.extend([nf_symbol_ce, nf_symbol_pe])
            time.sleep(2)

            current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            for each_order in self.kite.orders():
                if each_order['order_id'] == ce_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        trigger_price_nf = convert_to_tick_price(avg_sell_price + (avg_sell_price * sl_percent))
                        print("Placing CE Sl order for NF at", trigger_price_nf)

                        ce_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=nf_symbol_ce, buy_sell="buy", trigger_price= trigger_price_nf, price = trigger_price_nf + 20, quantity=qty)
                        if ce_sl_order_id!= -1:
                            self.sl_order_id_list.append(ce_sl_order_id)
                            if current_dt.hour == 9 and current_dt.minute == 16:
                                self.nf_9_16_expiry_dict[nf_symbol_ce] = ce_sl_order_id
                            elif current_dt.hour == 9 and current_dt.minute in [39, 40]:
                                self.nf_9_40_dict[nf_symbol_ce] = ce_sl_order_id
                            elif current_dt.hour == 10 and current_dt.minute in [44, 45]:
                                self.nf_10_45_dict[nf_symbol_ce] = ce_sl_order_id
                            elif current_dt.hour == 11 and current_dt.minute in [29, 30]:
                                self.nf_11_30_dict[nf_symbol_ce] = ce_sl_order_id
                            if self.buy_hedges_and_increase_quantity:
                                self.hedges_dict[ce_sl_order_id] = hedge_symbol_ce
                        else:
                            telegram_bot_sendtext("NIFTY straddle CE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext("NIFTY straddle CE option sell order is not filled!!!!!")

                if each_order['order_id'] == pe_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        trigger_price_nf = convert_to_tick_price(avg_sell_price + (avg_sell_price * sl_percent))
                        print("Placing PE Sl order for NF at", trigger_price_nf)
                        pe_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=nf_symbol_pe, buy_sell="buy", trigger_price= trigger_price_nf, price = trigger_price_nf + 20, quantity=qty)
                        if pe_sl_order_id!= -1:
                            self.sl_order_id_list.append(pe_sl_order_id)
                            if current_dt.hour == 9 and current_dt.minute == 16:
                                self.nf_9_16_expiry_dict[nf_symbol_pe] = pe_sl_order_id
                            elif current_dt.hour == 9 and current_dt.minute in [39, 40]:
                                self.nf_9_40_dict[nf_symbol_pe] = pe_sl_order_id
                            elif current_dt.hour == 10 and current_dt.minute in [44, 45]:
                                self.nf_10_45_dict[nf_symbol_pe] = pe_sl_order_id
                            elif current_dt.hour == 11 and current_dt.minute in [29, 30]:
                                self.nf_11_30_dict[nf_symbol_pe] = pe_sl_order_id
                            if self.buy_hedges_and_increase_quantity:
                                self.hedges_dict[pe_sl_order_id] = hedge_symbol_pe
                        else:
                            telegram_bot_sendtext("NIFTY straddle PE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext("NIFTY straddle PE option sell order is not filled!!!!!")
        except Exception as e:
            print("Unexpected error while shorting nf straddle. Error: "+str(e))
            telegram_bot_sendtext("Unexpected error while shorting nf straddle. Error: "+str(e))
            traceback.print_exc()

    
    def main(self):
        current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))

        if current_dt.hour < 14 or (current_dt.hour == 14 and current_dt.minute < 40):
            self.short_options_on_trigger()

        if not self.placed_nf_9_16_strangle and self.iso_week_day in [1, 3, 4] and current_dt.hour == 9 and current_dt.minute >=16:
            self.placed_nf_9_16_strangle = True
            if self.iso_week_day == 5:
                self.short_nifty_straddle(qty=self.nf_9_16_expiry_qty, sl_percent=0.25, strangle = True, strike_distance = 100)
            self.add_nf_strangle_to_watchlist('9_16_strangle', self.nf_9_16_qty)

        if not self.placed_bnf_9_20_straddle and current_dt.hour == 9 and (current_dt.minute >=20 or (current_dt.minute >=19 and current_dt.second >=54)):
            self.placed_bnf_9_20_straddle = True
            #self.short_bnf_straddle(25, 'percent_based')
            self.add_bnf_straddle_to_watchlist('9_20_straddle',self.bnf_9_20_qty)

        if not self.placed_nf_9_40_strangle and current_dt.hour == 9 and (current_dt.minute >=40 or (current_dt.minute >=39 and current_dt.second >=52)):
            self.placed_nf_9_40_strangle = True
            self.short_nifty_straddle(qty=self.nf_9_40_qty, sl_percent=0.35, strangle = True, strike_distance = 100)

        if not self.placed_bnf_10_05_strangle and current_dt.hour == 10 and current_dt.minute >=5:
            self.placed_bnf_10_05_strangle = True
            self.add_bnf_strangle_to_watchlist(strategy = '10_05_strangle', qty= self.bnf_10_05_qty, sl_percent=0.2)

        if not self.placed_nf_10_45_straddle and current_dt.hour == 10 and (current_dt.minute >=45 or (current_dt.minute >=44 and current_dt.second >=52)):
            self.placed_nf_10_45_straddle = True
            #self.short_nifty_straddle(50)
            self.short_nifty_straddle(qty=self.nf_10_45_qty, sl_percent=0.28, strangle = True, strike_distance = 50)

        if not self.placed_bnf_11_15_strangle and current_dt.hour == 11 and current_dt.minute >=15:
            self.placed_bnf_11_15_strangle = True
            self.add_bnf_strangle_to_watchlist(strategy = '11_15_strangle', qty=self.bnf_11_15_qty, sl_percent=0.18)

        if not self.placed_bnf_11_45_straddle and current_dt.hour == 11 and (current_dt.minute >=45 or (current_dt.minute >=44 and current_dt.second >=54)):
            self.placed_bnf_11_45_straddle = True
            #self.short_bnf_straddle(25, 'percent_based')
            self.add_bnf_straddle_to_watchlist('11_45_straddle', self.bnf_11_45_qty)

        if not self.placed_nf_11_30_strangle and current_dt.hour == 11 and (current_dt.minute >=30 or (current_dt.minute >=29 and current_dt.second >=52)):
            self.placed_nf_11_30_strangle = True
            self.short_nifty_straddle(qty=self.nf_11_30_qty, sl_percent=0.25, strangle = True, strike_distance = 50)

        if not self.placed_bnf_13_20_strangle and self.iso_week_day in [1, 2, 3, 4] and current_dt.hour == 13 and current_dt.minute >=20:
            self.placed_bnf_13_20_strangle = True
            self.short_bnf_straddle(qty= self.bnf_13_20_qty, sl_percent=0.25, strangle = True, strike_distance = 200)

        if self.iso_week_day == 5 and not self.exit_12_44_done and current_dt.hour == 12 and current_dt.minute >=44 and current_dt.second >=4:
            self.exit_12_44_done = True
            self.cancel_orders_and_exit_position(self.nf_9_16_expiry_dict, self.nf_9_16_expiry_qty)

        if not self.exit_14_55_done and current_dt.hour == 14 and (current_dt.minute >=55 or (current_dt.minute >=54 and current_dt.second >=54)):
            self.exit_14_55_done = True
            self.cancel_orders_and_exit_position(self.bnf_9_20_dict, self.bnf_9_20_qty)

        if not self.exit_15_00_done and current_dt.hour == 15 and current_dt.minute >=0 and current_dt.second >=4:
            self.exit_15_00_done = True
            self.cancel_orders_and_exit_position(self.bnf_11_15_dict, self.bnf_11_15_qty)
        
        if not self.exit_15_05_done and current_dt.hour == 15 and current_dt.minute >=5 and current_dt.second >=4:
            self.exit_15_05_done = True
            self.cancel_orders_and_exit_position(self.bnf_10_05_dict, self.bnf_10_05_qty)

        if not self.exit_15_08_done and current_dt.hour == 15 and current_dt.minute >=8 and current_dt.second >=4:
            self.exit_15_08_done = True
            self.cancel_orders_and_exit_position(self.nf_9_40_dict, self.nf_9_40_qty)

        if not self.exit_15_10_done and current_dt.hour == 15 and current_dt.minute >=10 and current_dt.second >=4:
            self.exit_15_10_done = True
            self.cancel_orders_and_exit_position(self.nf_10_45_dict, self.nf_10_45_qty)

        if not self.exit_15_12_done and current_dt.hour == 15 and current_dt.minute >=12 and current_dt.second >=4:
            self.exit_15_12_done = True
            self.cancel_orders_and_exit_position(self.bnf_11_45_dict, self.bnf_11_45_qty)

        if not self.exit_15_15_done and self.iso_week_day in [1, 3, 4] and current_dt.hour == 15 and current_dt.minute >=15 and current_dt.second >=4:
            self.exit_15_15_done = True
            self.cancel_orders_and_exit_position(self.nf_9_16_dict, self.nf_9_16_qty)

        if not self.exit_15_17_done and current_dt.hour == 15 and current_dt.minute >=17 and current_dt.second >=4:
            self.exit_15_17_done = True
            self.cancel_orders_and_exit_position(self.nf_11_30_dict, self.nf_11_30_qty)

        if not self.exit_15_19_done and self.iso_week_day in [1, 2, 3, 4] and current_dt.hour == 15 and current_dt.minute >=18 and current_dt.second >=40:
            self.exit_15_19_done = True
            self.cancel_orders_and_exit_position(self.bnf_13_20_dict, self.bnf_13_20_qty)
        
        if not self.exit_procedure_done and current_dt.hour == 15 and current_dt.minute >=19:
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

        if self.buy_hedges_and_increase_quantity:
            dt_now = datetime.datetime.now()
            time_difference = dt_now - self.last_orders_checked_dt
            if time_difference.seconds >= 6:
                self.last_orders_checked_dt = dt_now
                for each_order in self.kite.orders():
                    if each_order['order_id'] in self.hedges_dict.keys():
                        if each_order['status'] == 'COMPLETE' and each_order['order_id'] not in self.hedge_exit_sl_order_id_list:
                            if each_order['filled_quantity'] == each_order['quantity']:
                                self.hedge_exit_sl_order_id_list.append(each_order['order_id'])
                                qty = each_order['filled_quantity']
                                hedge_symbol = self.hedges_dict[each_order['order_id']]
                                self.orders_obj.place_market_order(symbol = hedge_symbol, buy_sell= 'sell', quantity=qty, use_limit_order = False)


    def cancel_orders_and_exit_position(self, symbols_dict, qty):
        for each_order in self.kite.orders():
            if each_order['order_id'] in symbols_dict.values():
                if each_order['status'] == 'TRIGGER PENDING':
                    self.orders_obj.cancel_order(each_order['order_id'])

                    for each_pos in self.kite.positions()['day']:
                        if each_pos['tradingsymbol'] in symbols_dict.keys() and each_pos['product'] == 'MIS' and each_pos['quantity'] != 0:
                            exit_quantity = qty
                            if self.buy_hedges_and_increase_quantity:
                                exit_quantity = qty * 3
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

    def add_itm_strangle_to_websocket(self, atm_strike, distance_from_atm = 200, index = 'BANKNIFTY'):
        ce_strike = atm_strike - distance_from_atm
        pe_strike = atm_strike + distance_from_atm
        if index == 'BANKNIFTY':
            ce_strike_list = [ce_strike - 100, ce_strike, ce_strike+ 100]
            pe_strike_list = [pe_strike - 100, pe_strike, pe_strike+ 100]
        elif index == 'NIFTY':
            ce_strike_list = [ce_strike - 50, ce_strike, ce_strike+ 50]
            pe_strike_list = [pe_strike - 50, pe_strike, pe_strike+ 50]

        tokens_list = []
        for each_strike in ce_strike_list:
            symbol_ce, token_ce = self.kite_functions.get_options_symbol_and_token(index, each_strike, 'CE')
            if token_ce not in self.nf_bnf_option_tokens:
                tokens_list.append(token_ce)
                self.nf_bnf_option_tokens.append(token_ce)

        for each_strike in pe_strike_list:
            symbol_pe, token_pe = self.kite_functions.get_options_symbol_and_token(index, each_strike, 'PE')
            if token_pe not in self.nf_bnf_option_tokens:
                tokens_list.append(token_pe)
                self.nf_bnf_option_tokens.append(token_pe)

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

    def add_bnf_strangle_to_watchlist(self, strategy, qty, sl_percent=0.2):
        try:
            banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
            bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            self.add_itm_strangle_to_websocket(atm_strike = bnf_atm_strike, distance_from_atm = 200, index = 'BANKNIFTY')
            banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
            bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            bnf_symbol_ce, bnf_token_ce = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike - 200, 'CE')
            bnf_symbol_pe, bnf_token_pe = self.kite_functions.get_options_symbol_and_token('BANKNIFTY', bnf_atm_strike + 200, 'PE')

            ltp_ce = eval(self.redis.get(str(bnf_token_ce)))
            ce_trigger_price = convert_to_tick_price(ltp_ce + (ltp_ce * sl_percent))
            ltp_pe = eval(self.redis.get(str(bnf_token_pe)))
            pe_trigger_price = convert_to_tick_price(ltp_pe + (ltp_pe * sl_percent))
            self.watchlist[strategy + 'ce'] = {'token': bnf_token_ce,'symbol': bnf_symbol_ce,'price': ltp_ce, 'trigger_price': ce_trigger_price,
                                            'datetime': datetime.datetime.now(), 'opposite_key':strategy + 'pe', 'quantity':qty}
            self.watchlist[strategy + 'pe'] = {'token': bnf_token_pe,'symbol': bnf_symbol_pe,'price': ltp_pe, 'trigger_price': pe_trigger_price,
                                            'datetime': datetime.datetime.now(), 'opposite_key':strategy + 'ce', 'quantity':qty}

        except Exception as e:
            print("Unexpected error in add_bnf_strangle_to_watchlist. Error: "+str(e))
            telegram_bot_sendtext("Unexpected error in add_bnf_strangle_to_watchlist. Error: "+str(e))
            traceback.print_exc()


    def add_nf_strangle_to_watchlist(self, strategy, qty):
        try:
            nifty_ltp = eval(self.redis.get(str(self.nifty_token)))
            nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
            self.add_itm_strangle_to_websocket(atm_strike = nf_atm_strike, distance_from_atm = 100, index = 'NIFTY')
            nifty_ltp = eval(self.redis.get(str(self.nifty_token)))
            nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
            nf_symbol_ce, nf_token_ce = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike - 100, 'CE')
            nf_symbol_pe, nf_token_pe = self.kite_functions.get_options_symbol_and_token('NIFTY', nf_atm_strike + 100, 'PE')

            ltp_ce = eval(self.redis.get(str(nf_token_ce)))
            ce_trigger_price = convert_to_tick_price(ltp_ce + (ltp_ce * .25))
            ltp_pe = eval(self.redis.get(str(nf_token_pe)))
            pe_trigger_price = convert_to_tick_price(ltp_pe + (ltp_pe * .25))
            self.watchlist[strategy + 'ce'] = {'token': nf_token_ce,'symbol': nf_symbol_ce,'price': ltp_ce, 'trigger_price': ce_trigger_price,
                                            'datetime': datetime.datetime.now(), 'opposite_key':strategy + 'pe', 'quantity':qty}
            self.watchlist[strategy + 'pe'] = {'token': nf_token_pe,'symbol': nf_symbol_pe,'price': ltp_pe, 'trigger_price': pe_trigger_price,
                                            'datetime': datetime.datetime.now(), 'opposite_key':strategy + 'ce', 'quantity':qty}

        except Exception as e:
            print("Unexpected error in add_nf_strangle_to_watchlist. Error: "+str(e))
            telegram_bot_sendtext("Unexpected error in add_nf_strangle_to_watchlist. Error: "+str(e))
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
            if self.buy_hedges_and_increase_quantity:
                qty = qty * 3
                hedge_symbol, hedge_token = self.get_hedge_symbol(symbol)
                if hedge_symbol == None:
                    telegram_bot_sendtext(f"Hedge Symbol is None for {symbol}. Straddle entry time is {dt}")
                else:
                    hedge_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol, buy_sell= "buy", quantity=qty, use_limit_order = False)
                    self.traded_symbols_list.append(hedge_symbol)
                    time.sleep(1)
                
            order_id = self.orders_obj.place_market_order(symbol = symbol, buy_sell= "sell", quantity=qty)
            self.traded_symbols_list.append(symbol)
            strategy_entry_hour = None
            strategy_entry_minute = None
            sl_points = 160
            if dt.hour == 9 and dt.minute == 16:
                self.nf_9_16_dict[symbol] = None
                strategy_entry_hour = 9
                strategy_entry_minute = 16
            elif dt.hour == 9 and dt.minute in [19, 20]:
                self.bnf_9_20_dict[symbol] = None
                strategy_entry_hour = 9
                strategy_entry_minute = 20
                sl_points = 80
            elif dt.hour == 10 and dt.minute in [4, 5]:
                self.bnf_10_05_dict[symbol] = None
                strategy_entry_hour = 10
                strategy_entry_minute = 5
                sl_points = 100
            elif dt.hour == 11 and dt.minute in [14, 15]:
                self.bnf_11_15_dict[symbol] = None
                strategy_entry_hour = 11
                strategy_entry_minute = 15
            elif dt.hour == 11 and dt.minute in [44, 45]:
                self.bnf_11_45_dict[symbol] = None
                strategy_entry_hour = 11
                strategy_entry_minute = 45
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
                            sl_price = round(sl_price, 1)
                            telegram_bot_sendtext(f"Placing Sl order for {strategy_entry_hour} {strategy_entry_minute} {symbol} at {sl_price}")

                            sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=symbol, buy_sell="buy", trigger_price= sl_price, price = sl_price + 20, quantity=qty)
                            if sl_order_id!= -1:
                                sl_order_is_placed = True
                                self.sl_order_id_list.append(sl_order_id)
                                if strategy_entry_hour == 9 and strategy_entry_minute == 16:
                                    self.nf_9_16_dict[symbol] = sl_order_id
                                elif strategy_entry_hour == 9 and strategy_entry_minute == 20:
                                    self.bnf_9_20_dict[symbol] = sl_order_id
                                elif strategy_entry_hour == 10 and strategy_entry_minute == 5:
                                    self.bnf_10_05_dict[symbol] = sl_order_id
                                elif strategy_entry_hour == 11 and strategy_entry_minute == 15:
                                    self.bnf_11_15_dict[symbol] = sl_order_id
                                elif strategy_entry_hour == 11 and strategy_entry_minute == 45:
                                    self.bnf_11_45_dict[symbol] = sl_order_id
                                if self.buy_hedges_and_increase_quantity:
                                    self.hedges_dict[sl_order_id] = hedge_symbol
                            else:
                                print(f"Sl order for {symbol} at {sl_price} is not Placed!!!!!")
                        else:
                            print(f"{symbol} option sell order is not filled!!!!!")

            if not sl_order_is_placed:
                telegram_bot_sendtext(f"{symbol} option sell order is not filled!!!!!")


    def get_hedge_symbol(self, symbol):
        try:
            strike, underlying_name = self.kite_functions.get_option_strike_and_underlying_name_from_symbol(symbol)
            if underlying_name == 'BANKNIFTY':
                starting_distance = 200
                strike_difference = 100
            elif underlying_name == 'NIFTY':
                if str(int(strike))[-2] == '5':
                    strike += 50
                starting_distance = 200
                strike_difference = 100
            ce_pe = symbol[-2:]
            otm_symbols_list = []
            if ce_pe == 'CE':
                otm_strike = strike + starting_distance
                for _ in range(20):
                    nf_bnf_symbol_ce, bnf_token_ce = self.kite_functions.get_options_symbol_and_token(underlying_name, otm_strike, 'CE')
                    # If symbol is not present in instrument_df stop
                    if nf_bnf_symbol_ce == None:
                        break
                    #filter out 100, 400 and 900 strikes. idx is -5 because ends with CE
                    if not (underlying_name == 'BANKNIFTY' and str(otm_strike)[-5] in ['1', '4', '9']):
                        otm_symbols_list.append('NFO:'+nf_bnf_symbol_ce)
                    otm_strike += strike_difference
            
            elif ce_pe == 'PE':
                otm_strike = strike - starting_distance
                for _ in range(20):
                    nf_bnf_symbol_pe, bnf_token_ce = self.kite_functions.get_options_symbol_and_token(underlying_name, otm_strike, 'PE')
                    # If symbol is not present in instrument_df stop
                    if nf_bnf_symbol_pe == None:
                        break
                    #filter out 100, 400 and 900 strikes. idx is -5 because ends with PE
                    if not (underlying_name == 'BANKNIFTY' and str(otm_strike)[-5] in ['1', '4', '9']):
                        otm_symbols_list.append('NFO:'+nf_bnf_symbol_pe)
                    otm_strike -= strike_difference
                
            ltp_list = ['NFO:'+symbol]
            ltp_list.extend(otm_symbols_list)
            ltp_dict = self.kite.ltp([ltp_list])
            symbol_ltp = ltp_dict['NFO:'+symbol]['last_price']
            max_hedge_ltp = symbol_ltp * 0.05
            hedge_symbol =  None
            hedge_token = None
            for key, values in ltp_dict.items():
                if values['last_price'] < max_hedge_ltp:
                    hedge_symbol = key[4:]
                    hedge_token = values['instrument_token']
                    #Key are sorted hence break is required for CE
                    if ce_pe == 'CE':
                        break
            #if no symbol meets criteria return the last item in ltp_list 
            if hedge_symbol ==  None:
                print("Hedge symbol is None for", symbol)
                hedge_symbol = ltp_list[-1][4:]
                hedge_token = ltp_dict[ltp_list[-1]]['instrument_token']
            
            return hedge_symbol, hedge_token
        except Exception as e:
            print(f"Unexpected error while finding hedge for {symbol}. Error: "+str(e))
            telegram_bot_sendtext(f"Unexpected error while finding hedge for {symbol}. Error: "+str(e))
            traceback.print_exc()
            return None, None