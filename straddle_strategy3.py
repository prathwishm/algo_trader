import datetime
import math
import pytz
import traceback
import time
import gspread
from convert_float_to_tick_price import convert_to_tick_price
from telegram_bot import telegram_bot_sendtext
from straddle_strategy3_list import trades_list, NRML_DAYS
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('straddle_strategy3_error.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(file_handler)

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THRUSDAY = 4
FRIDAY = 5

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

def check_if_time_is_allowed(current_dt, given_time):
    return current_dt.hour == given_time[0] and current_dt.minute >= given_time[1] and (current_dt.second >= given_time[2] or current_dt.minute > given_time[1])

class straddles:
    def __init__(self, kite, kite_func, orders_obj, redis_obj, ticker, margin):
        self.kite = kite
        self.kite_functions = kite_func
        self.max_trade_margin = margin
        self.orders_obj = orders_obj
        self.redis = redis_obj
        self.ticker = ticker
        self.sl_order_id_list = []
        self.traded_symbols_list = []
        self.exit_procedure_done = False
        self.nf_bnf_option_tokens = []
        self.watchlist = {}
        self.target_watchlist = {}

        self.nifty_token = kite_func.get_symbol_token('NSE:NIFTY 50')
        self.bank_nifty_token = kite_func.get_symbol_token('NSE:NIFTY BANK')
        self.fin_nifty_token = kite_func.get_symbol_token('NSE:NIFTY FIN SERVICE')
        self.nf_bnf_option_tokens.extend([self.nifty_token, self.bank_nifty_token, self.fin_nifty_token])
        self.iso_week_day = datetime.date.today().isoweekday()

        self.trades_list = trades_list
        self.trades_placed = []
        self.trades_exited = []
        self.trades_dict = {}

        self.running_pnl_done = {}

        self.exit_15_19_done = False
        self.add_straddle_strangle_to_websocket = False
        self.last_orders_checked_dt = datetime.datetime.now()
        if self.iso_week_day in [3,4]:
            self.add_straddle_strangle_to_websocket = True
        self.hedges_dict = {}
        self.hedge_exit_sl_order_id_list = []

        sa = gspread.service_account(filename='gsheetes-project-1bb0d0a4d7a8.json')
        sh = sa.open("algo_tradelog")
        self.wks = sh.worksheet("Prasad_detailed")
        self.wks_pnl = sh.worksheet("Prasad_summary")
        self.wks_running_pnl = sh.worksheet("Prasad_R_PNL")
        self.wks.append_row(['-'])
        self.wks_pnl.append_row(['-'])
        self.wks_running_pnl.append_row(['-'])

    def set_target_trigger_price(self, strategy, option_type, sl_order_id, token, qty, target_price, trigger_price, limit_price):
        try:
            print(f"Setting target trigger price for {strategy} {option_type}")
            target_tick_price = convert_to_tick_price(target_price)
            self.target_watchlist[strategy + option_type] = {
                'token': token,
                'order_id': sl_order_id,
                'target_price': target_tick_price,
                'limit_price': limit_price,
                'trigger_price': trigger_price,
                'datetime': datetime.datetime.now(),
                'quantity': qty
            }
        except Exception as e:
            logger.exception("Unexpected error while set_target_trigger_price. Error: "+str(e))
            telegram_bot_sendtext("Unexpected error while set_target_trigger_price. Error: "+str(e))
            traceback.print_exc()

    def short_straddle(self, strategy_details, execution_day_details):
        try:
            if strategy_details['instrument_type'] == 'NIFTY':
                instrument_token = self.nifty_token
                instrument_ltp = eval(self.redis.get(str(instrument_token)))
                atm_strike = get_nifty_atm_strike(instrument_ltp)
                strike_distance = 100 if 'strike_distance' not in strategy_details else strategy_details['strike_distance']
                trigger_price_buffer = 20
            elif strategy_details['instrument_type'] == 'BANKNIFTY':
                instrument_token = self.bank_nifty_token
                instrument_ltp = eval(self.redis.get(str(instrument_token)))
                atm_strike = get_banknifty_atm_strike(instrument_ltp)
                strike_distance = 200 if 'strike_distance' not in strategy_details else strategy_details['strike_distance']
                trigger_price_buffer = 40
            elif strategy_details['instrument_type'] == 'FINNIFTY':
                instrument_token = self.fin_nifty_token
                instrument_ltp = eval(self.redis.get(str(instrument_token)))
                atm_strike = get_banknifty_atm_strike(instrument_ltp)
                strike_distance = 200 if 'strike_distance' not in strategy_details else strategy_details['strike_distance']
                trigger_price_buffer = 40

            use_mis_order = self.iso_week_day not in NRML_DAYS

            strategy_name = strategy_details['strategy_name']
            strangle = False if 'strangle' not in strategy_details else strategy_details['strangle']
            buy_hedges = False if 'hedge_multiplier' not in execution_day_details else True
            target_percent = 0.25 if 'target_percent' not in execution_day_details else execution_day_details['target_percent']
            qty = strategy_details['quantity'] * execution_day_details['quantity_multiplier']
            current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))

            if strangle:
                self.add_itm_strangle_to_websocket(atm_strike, strike_distance, strategy_details['instrument_type'])
                instrument_symbol_ce, instrument_token_ce = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike - strike_distance, 'CE')
                instrument_symbol_pe, instrument_token_pe = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike + strike_distance, 'PE')
            else:
                self.add_itm_strangle_to_websocket(atm_strike, 0, strategy_details['instrument_type'])
                instrument_symbol_ce, instrument_token_ce = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike, 'CE')
                instrument_symbol_pe, instrument_token_pe = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike, 'PE')
            
            if buy_hedges:
                qty = qty * execution_day_details['hedge_multiplier']
                hedge_symbol_ce, hedge_token_ce = self.get_hedge_symbol(instrument_symbol_ce)
                hedge_symbol_pe, hedge_token_pe = self.get_hedge_symbol(instrument_symbol_pe)
                hedge_ce_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol_ce, buy_sell= "buy", quantity=qty, use_limit_order = False, use_mis_order = use_mis_order)
                hedge_pe_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol_pe, buy_sell= "buy", quantity=qty, use_limit_order = False, use_mis_order = use_mis_order)
                self.traded_symbols_list.extend([hedge_symbol_ce, hedge_symbol_pe])
                time.sleep(1)

            ce_order_id = self.orders_obj.place_market_order(symbol = instrument_symbol_ce, buy_sell= "sell", quantity=qty, use_limit_order = True, use_mis_order = use_mis_order)
            pe_order_id = self.orders_obj.place_market_order(symbol = instrument_symbol_pe, buy_sell= "sell", quantity=qty, use_limit_order = True, use_mis_order = use_mis_order)
            self.traded_symbols_list.extend([instrument_symbol_ce, instrument_symbol_pe])
            time.sleep(2)
            orders_placed = []

            for each_order in self.kite.orders():
                if each_order['order_id'] == ce_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        sl_diff_price = avg_sell_price * strategy_details['sl_percent']
                        target_price = convert_to_tick_price(avg_sell_price * target_percent)
                        trigger_price = convert_to_tick_price(avg_sell_price + sl_diff_price)
                        print(f"Placing CE Sl order for {strategy_details['instrument_type']} at {trigger_price}")

                        ce_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=instrument_symbol_ce, buy_sell="buy", trigger_price = trigger_price, price = trigger_price + trigger_price_buffer, quantity=qty, use_mis_order = use_mis_order)
                        ce_dict = {
                            'date':str(current_dt.date()),
                            'strategy': strategy_name,
                            'entry_time':str(current_dt.time()),
                            'symbol': instrument_symbol_ce,
                            'sell_price': each_order['average_price'],
                            'qty': each_order['quantity'],
                            'sl_id': ce_sl_order_id,
                            'sl_price':trigger_price,
                            'buy_price': None,
                            'exit_time': None,
                            'sl_hit':False
                        }
                        orders_placed.append(ce_dict)

                        if ce_sl_order_id != -1:
                            self.sl_order_id_list.append(ce_sl_order_id)
                            if strategy_name not in self.trades_dict: 
                                self.trades_dict[strategy_name] = {}
                            self.trades_dict[strategy_name][instrument_symbol_ce] = ce_sl_order_id
                            self.trades_dict[strategy_name]['ce_details'] = ce_dict
                            self.set_target_trigger_price(strategy_name, "CE", ce_sl_order_id, instrument_token_ce, qty, target_price, target_price * 2, (target_price * 2) + trigger_price_buffer)
                            if buy_hedges:
                                self.hedges_dict[ce_sl_order_id] = hedge_symbol_ce
                        else:
                            telegram_bot_sendtext(f"{strategy_details['instrument_type']} straddle CE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext(f"{strategy_details['instrument_type']} straddle CE option sell order is not filled!!!!!")
                
                if each_order['order_id'] == pe_order_id:
                    if each_order['status'] == 'COMPLETE':
                        avg_sell_price = each_order['average_price']
                        sl_diff_price = avg_sell_price * strategy_details['sl_percent']
                        target_price = convert_to_tick_price(avg_sell_price * target_percent)
                        trigger_price = convert_to_tick_price(avg_sell_price + sl_diff_price)
                        print(f"Placing PE Sl order for {strategy_details['instrument_type']} at {trigger_price}")
                        pe_sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=instrument_symbol_pe, buy_sell="buy", trigger_price= trigger_price, price = trigger_price + trigger_price_buffer, quantity=qty, use_mis_order = use_mis_order)
                        pe_dict = {
                            'date':str(current_dt.date()),
                            'strategy': strategy_name,
                            'entry_time':str(current_dt.time()),
                            'symbol': instrument_symbol_pe,
                            'sell_price': each_order['average_price'],
                            'qty': each_order['quantity'],
                            'sl_id': pe_sl_order_id,
                            'sl_price':trigger_price,
                            'buy_price': None,
                            'exit_time': None,
                            'sl_hit':False
                        }
                        orders_placed.append(pe_dict)
                        if pe_sl_order_id!= -1:
                            self.sl_order_id_list.append(pe_sl_order_id)
                            if strategy_name not in self.trades_dict: 
                                self.trades_dict[strategy_name] = {}
                            self.trades_dict[strategy_name][instrument_symbol_pe] = pe_sl_order_id
                            self.trades_dict[strategy_name]['pe_details'] = pe_dict
                            self.set_target_trigger_price(strategy_name, "PE", pe_sl_order_id, instrument_token_pe, qty, target_price, target_price * 2, (target_price * 2) + trigger_price_buffer)
                            if buy_hedges:
                                self.hedges_dict[pe_sl_order_id] = hedge_symbol_pe
                        else:
                            telegram_bot_sendtext(f"{strategy_details['instrument_type']} straddle PE option Stop Loss order is not Placed!!!!!")
                    else:
                        telegram_bot_sendtext(f"{strategy_details['instrument_type']} straddle PE option sell order is not filled!!!!!")

            self.send_orders_details(orders_placed, strategy_name)
        except Exception as e:
            logger.exception(f"Unexpected error while shorting {strategy_details['instrument_type']} straddle. Error: "+str(e))
            telegram_bot_sendtext(f"Unexpected error while shorting {strategy_details['instrument_type']} straddle. Error: "+str(e))
            traceback.print_exc()

    def send_orders_details(self, orders_placed, strategy_name):
        try:
            msg_text = "Placed stategy " + strategy_name + "\n"
            
            for each_order in orders_placed:
                msg_text = msg_text + f"{each_order['symbol']} @ {each_order['sell_price']} - SL {each_order['sl_price']}\n"
            telegram_bot_sendtext(msg_text)

        except Exception as e:
            logger.exception(f"Unexpected error while send_orders_details. Error: "+str(e))
            telegram_bot_sendtext(f"Unexpected error while send_orders_details. Error: "+str(e))
            traceback.print_exc()

    def cancel_orders_and_exit_position(self, strategy_details, execution_day_details, symbols_dict):
        exited_symbols = [] #Used to prevent exiting of same symbol from a different strategy
        exited_order_ids = []
        buy_hedges = False if 'hedge_multiplier' not in execution_day_details else True
        qty = strategy_details['quantity'] * execution_day_details['quantity_multiplier']
        use_mis_order = self.iso_week_day not in NRML_DAYS

        if buy_hedges:
            qty = qty * execution_day_details['hedge_multiplier']

        telegram_bot_sendtext(f"Exiting strategy {strategy_details['strategy_name']}")

        for each_order in self.kite.orders():
            if each_order['order_id'] in symbols_dict.values():
                if each_order['status'] == 'TRIGGER PENDING':
                    self.orders_obj.cancel_order(each_order['order_id'])

                    for each_pos in self.kite.positions()['day']:
                        if each_pos['tradingsymbol'] in symbols_dict.keys() and each_pos['product'] == 'MIS' and each_pos['quantity'] != 0 and each_pos['tradingsymbol'] not in exited_symbols:
                            exit_quantity = qty
                            exit_type = "sell" if each_pos['quantity'] > 0 else "buy"
                            if exit_quantity > 0:
                                exit_order_id = self.orders_obj.place_market_order(symbol = each_pos['tradingsymbol'], buy_sell= exit_type, quantity=exit_quantity, use_limit_order = True, use_mis_order = use_mis_order)
                                exited_order_ids.append(exit_order_id)
                                exited_symbols.append(each_pos['tradingsymbol'])
                
                elif each_order['status'] == 'COMPLETE':
                    self.update_trade_details(each_order, symbols_dict, sl_hit = True)
                    
        time.sleep(2)
        for each_order in self.kite.orders():
            if each_order['order_id'] in exited_order_ids:
                self.update_trade_details(each_order, symbols_dict, sl_hit = False)

    def update_trade_details(self, each_order, symbols_dict, sl_hit = False):
        try:
            strategy_data = []
            logger.info(f"Updating order details for {each_order['tradingsymbol']}")
            if each_order['tradingsymbol'][-2:] == 'CE':
                symbols_dict['ce_details']['buy_price'] = each_order['average_price']
                symbols_dict['ce_details']['exit_time'] = each_order['exchange_update_timestamp'].split()[1]
                symbols_dict['ce_details']['sl_hit'] = sl_hit
                pnl = (symbols_dict['ce_details']['sell_price'] - symbols_dict['ce_details']['buy_price']) * symbols_dict['ce_details']['qty']
                symbols_dict['ce_details']['pnl'] = math.floor(pnl)
                strategy_data = list(symbols_dict['ce_details'].values())
            elif each_order['tradingsymbol'][-2:] == 'PE':
                symbols_dict['pe_details']['buy_price'] = each_order['average_price']
                symbols_dict['pe_details']['exit_time'] = each_order['exchange_update_timestamp'].split()[1]
                symbols_dict['pe_details']['sl_hit'] = sl_hit
                pnl = (symbols_dict['pe_details']['sell_price'] - symbols_dict['pe_details']['buy_price']) * symbols_dict['pe_details']['qty']
                symbols_dict['pe_details']['pnl'] = math.floor(pnl)
                strategy_data = list(symbols_dict['pe_details'].values())
            logger.info(strategy_data)
            self.wks.append_row(strategy_data)
        except Exception as e:
            logger.exception("Unexpected error in update_trade_details. Error: "+str(e))
            telegram_bot_sendtext("Unexpected error in update_trade_details. Error: "+str(e))
            traceback.print_exc()

    def add_itm_strangle_to_websocket(self, atm_strike, distance_from_atm = 200, index = 'BANKNIFTY'):
        ce_strike = atm_strike - distance_from_atm
        pe_strike = atm_strike + distance_from_atm
        if index == 'BANKNIFTY' or index == 'FINNIFTY':
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
            logger.info(f'ADDING {tokens_list} to websocket')
            self.ticker.subscribe_tokens(tokens_list)
            time.sleep(5)

    def add_to_watchlist(self, strategy_details, execution_day_details):
        try:
            if strategy_details['instrument_type'] == 'NIFTY':
                instrument_token = self.nifty_token
                instrument_ltp = eval(self.redis.get(str(instrument_token)))
                atm_strike = get_nifty_atm_strike(instrument_ltp)
                strike_distance = 100 if 'strike_distance' not in strategy_details else strategy_details['strike_distance']
                sl_percent = 0.25 if 'sl_percent' not in strategy_details else strategy_details['sl_percent']

            elif strategy_details['instrument_type'] == 'BANKNIFTY':
                instrument_token = self.bank_nifty_token
                instrument_ltp = eval(self.redis.get(str(instrument_token)))
                atm_strike = get_banknifty_atm_strike(instrument_ltp)
                strike_distance = 200 if 'strike_distance' not in strategy_details else strategy_details['strike_distance']
                sl_percent = 0.2 if 'sl_percent' not in strategy_details else strategy_details['sl_percent']

            elif strategy_details['instrument_type'] == 'FINNIFTY':
                instrument_token = self.fin_nifty_token
                instrument_ltp = eval(self.redis.get(str(instrument_token)))
                atm_strike = get_banknifty_atm_strike(instrument_ltp)
                strike_distance = 200 if 'strike_distance' not in strategy_details else strategy_details['strike_distance']
                sl_percent = 0.2 if 'sl_percent' not in strategy_details else strategy_details['sl_percent']

            strategy_name = strategy_details['strategy_name']
            strangle = False if 'strangle' not in strategy_details else strategy_details['strangle']
            buy_hedges = False if 'hedge_multiplier' not in execution_day_details else True
            qty = strategy_details['quantity'] * execution_day_details['quantity_multiplier']

            if buy_hedges:
                qty = qty * execution_day_details['hedge_multiplier']

            if strangle:
                self.add_itm_strangle_to_websocket(atm_strike = atm_strike, distance_from_atm = strike_distance, index = strategy_details['instrument_type'])
                instrument_symbol_ce, instrument_token_ce = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike - strike_distance, 'CE')
                instrument_symbol_pe, instrument_token_pe = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike + strike_distance, 'PE')
            else:
                self.add_itm_strangle_to_websocket(atm_strike, 0, strategy_details['instrument_type'])
                instrument_symbol_ce, instrument_token_ce = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike, 'CE')
                instrument_symbol_pe, instrument_token_pe = self.kite_functions.get_options_symbol_and_token(strategy_details['instrument_type'], atm_strike, 'PE')
            
            ltp_ce = eval(self.redis.get(str(instrument_token_ce)))
            ce_trigger_price = convert_to_tick_price(ltp_ce + (ltp_ce * sl_percent))
            ltp_pe = eval(self.redis.get(str(instrument_token_pe)))
            pe_trigger_price = convert_to_tick_price(ltp_pe + (ltp_pe * sl_percent))

            self.watchlist[strategy_name + 'ce'] = {
                'token': instrument_token_ce,
                'symbol': instrument_symbol_ce,
                'price': ltp_ce,
                'trigger_price': ce_trigger_price,
                'datetime': datetime.datetime.now(),
                'opposite_key':strategy_name + 'pe',
                'buy_hedges': buy_hedges,
                'quantity':qty
            }
            self.watchlist[strategy_name + 'pe'] = {
                'token': instrument_token_pe,
                'symbol': instrument_symbol_pe,
                'price': ltp_pe,
                'trigger_price': pe_trigger_price,
                'datetime': datetime.datetime.now(),
                'opposite_key':strategy_name + 'ce',
                'buy_hedges': buy_hedges,
                'quantity':qty
            }

            telegram_bot_sendtext(f"Watch list created for {strategy_details['instrument_type']}-{strategy_name}.\n {atm_strike} CE - {ce_trigger_price}\n {atm_strike} PE - {pe_trigger_price}")

        except Exception as e:
            logger.exception(f"Unexpected error in add_to_watchlist for {strategy_details['instrument_type']}. Error: "+str(e))
            telegram_bot_sendtext(f"Unexpected error in add_to_watchlist for {strategy_details['instrument_type']}. Error: "+str(e))
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
                    buy_hedges = values_dict['buy_hedges']
                    list_of_tokens_to_pop_from_watchlist.append(opposite_key)
                    symbol = self.watchlist[opposite_key]['symbol']
                    sl_price = self.watchlist[opposite_key]['trigger_price']
                    # if '9' in strategy_option:
                    #     sl_price = min(self.watchlist[opposite_key]['trigger_price'], tick_list[1]+80)
                    # else:
                    #     sl_price = min(self.watchlist[opposite_key]['trigger_price'], tick_list[1]+120)
                    qty = self.watchlist[opposite_key]['quantity']
                    self.short_option_and_place_sl(strategy = strategy_option[:-2],symbol=symbol, sl_price=sl_price, qty=qty, dt = values_dict['datetime'], buy_hedges=buy_hedges)

                    #self.watchlist.pop(opposite_key)
                    #list_of_tokens_to_pop_from_watchlist.append(opposite_key)
                    #place orders
                    
                    break

        for strat_option in list_of_tokens_to_pop_from_watchlist:
            try:
                self.watchlist.pop(strat_option)
            except Exception as e:
                logger.exception(f"Unexpected error while popping {strat_option} from watchlist. Error: "+str(e))
                telegram_bot_sendtext(f"Unexpected error while popping {strat_option} from watchlist. Error: "+str(e))
                traceback.print_exc()

    def check_for_target_hits(self):
        list_of_tokens_to_pop_from_target_watchlist = []
        open_orders = []
        for each_order in self.kite.orders():
            if each_order['status'] == 'TRIGGER PENDING':
                open_orders.append(each_order['order_id'])

        for strategy_option, values_dict in self.target_watchlist.items():
            if values_dict['order_id'] not in open_orders:
                print(f"check_for_target_hits :: order not open, hence popping {strategy_option}")
                list_of_tokens_to_pop_from_target_watchlist.append(strategy_option)
            else:
                ltp_data = list(map(eval, self.redis.lrange(str(values_dict['token'])+'_data', -25, -1)))
                for tick_list in ltp_data:
                    if tick_list[1] < values_dict['target_price'] and tick_list[0] > values_dict['datetime']:
                        list_of_tokens_to_pop_from_target_watchlist.append(strategy_option)
                        self.orders_obj.modify_sl_order(values_dict['order_id'], values_dict['quantity'], values_dict['limit_price'], values_dict['trigger_price'])
                        telegram_bot_sendtext(f"Updated target for {strategy_option} to {values_dict['trigger_price']}")
                        print(f"check_for_target_hits :: target updated for {strategy_option}")
                        break

        for strat_option in list_of_tokens_to_pop_from_target_watchlist:
            try:
                self.target_watchlist.pop(strat_option)
            except Exception as e:
                logger.exception(f"Unexpected error while popping {strat_option} from target_watchlist. Error: "+str(e))
                telegram_bot_sendtext(f"Unexpected error while popping {strat_option} from target_watchlist. Error: "+str(e))
                traceback.print_exc()

    def short_option_and_place_sl(self, strategy, symbol, sl_price, qty, dt, buy_hedges = False):

            use_mis_order = self.iso_week_day not in NRML_DAYS

            if buy_hedges:
                hedge_symbol, hedge_token = self.get_hedge_symbol(symbol)
                if hedge_symbol == None:
                    telegram_bot_sendtext(f"Hedge Symbol is None for {symbol}. Straddle entry time is {dt}")
                else:
                    hedge_order_id = self.orders_obj.place_market_order(symbol = hedge_symbol, buy_sell= "buy", quantity=qty, use_limit_order = False, use_mis_order = use_mis_order)
                    self.traded_symbols_list.append(hedge_symbol)
                    time.sleep(1)
                
            order_id = self.orders_obj.place_market_order(symbol = symbol, buy_sell= "sell", quantity=qty, use_limit_order = True, use_mis_order = use_mis_order)
            current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            self.traded_symbols_list.append(symbol)
            sl_points = 160
            if strategy not in self.trades_dict: 
                self.trades_dict[strategy] = {}
            self.trades_dict[strategy][symbol] = None
            time.sleep(1)
            sl_order_is_placed = False
            orders_placed = []
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
                            telegram_bot_sendtext(f"Placing Sl order for {strategy} - {symbol} at {sl_price}")

                            sl_order_id = self.orders_obj.place_sl_order_for_options(symbol=symbol, buy_sell="buy", trigger_price= sl_price, price = sl_price + 20, quantity=qty, use_mis_order = use_mis_order)
                            trade_dict = {'date':str(current_dt.date()), 'strategy': strategy,'entry_time':str(current_dt.time()), 'symbol': symbol,'sell_price': each_order['average_price'], 'qty': each_order['quantity'], 'sl_id': sl_order_id,
                                    'sl_price':sl_price,'buy_price': None, 'exit_time': None,'sl_hit':False}
                            if symbol[-2:] == 'CE':
                                key_name = 'ce_details'
                            else:
                                key_name = 'pe_details'
                            
                            order_dict = {
                                'date':str(current_dt.date()),
                                'strategy': strategy,
                                'entry_time':str(current_dt.time()),
                                'symbol': symbol,
                                'sell_price': avg_sell_price,
                                'qty': qty,
                                'sl_id': sl_order_id,
                                'sl_price':sl_price,
                                'buy_price': None,
                                'exit_time': None,
                                'sl_hit':False
                            }
                            orders_placed.append(order_dict)

                            if sl_order_id!= -1:
                                sl_order_is_placed = True
                                self.sl_order_id_list.append(sl_order_id)
                                self.trades_dict[strategy][symbol] = sl_order_id
                                self.trades_dict[strategy][key_name] = trade_dict
                                if buy_hedges:
                                    self.hedges_dict[sl_order_id] = hedge_symbol
                            else:
                                print(f"Sl order for {symbol} at {sl_price} is not Placed!!!!!")
                        else:
                            print(f"{symbol} option sell order is not filled!!!!!")

            if not sl_order_is_placed:
                telegram_bot_sendtext(f"{symbol} option sell order is not filled!!!!!")
            
            self.send_orders_details(orders_placed, strategy)

    def get_hedge_symbol(self, symbol):
        try:
            strike, underlying_name = self.kite_functions.get_option_strike_and_underlying_name_from_symbol(symbol)
            if underlying_name == 'BANKNIFTY':
                starting_distance = 300
                strike_difference = 100
                banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
                atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            elif underlying_name == 'NIFTY':
                if str(int(strike))[-2] == '5':
                    strike += 50
                starting_distance = 100
                strike_difference = 100
                nifty_ltp = eval(self.redis.get(str(self.nifty_token)))
                atm_strike = get_nifty_atm_strike(nifty_ltp)
            elif underlying_name == 'FINNIFTY':
                starting_distance = 200
                strike_difference = 100
                fin_nifty_ltp = eval(self.redis.get(str(self.fin_nifty_token)))
                atm_strike = get_banknifty_atm_strike(fin_nifty_ltp)
            
            ce_pe = symbol[-2:]
            otm_symbols_list = []
            if ce_pe == 'CE':
                if strike < atm_strike:
                    # Reduce hedging cost for itm options
                    strike = atm_strike
                    symbol, symbol_token = self.kite_functions.get_options_symbol_and_token(underlying_name, atm_strike, 'CE')
                otm_strike = strike + starting_distance
                if str(int(otm_strike))[-2] == '5': #fix for itm strikes where atm strike is multiple of 50
                    otm_strike += 50
                for _ in range(20):
                    nf_bnf_symbol_ce, bnf_token_ce = self.kite_functions.get_options_symbol_and_token(underlying_name, otm_strike, 'CE')
                    # If symbol is not present in instrument_df stop
                    if nf_bnf_symbol_ce == None:
                        break
                    #filter out 100, 400 and 900 strikes. idx is -5 because ends with CE
                    if not ((underlying_name == 'BANKNIFTY' or underlying_name == 'FINNIFTY') and str(otm_strike)[-5] in ['1', '4', '9']):
                        otm_symbols_list.append('NFO:'+nf_bnf_symbol_ce)
                    otm_strike += strike_difference
            
            elif ce_pe == 'PE':
                if strike > atm_strike:
                    # Reduce hedging cost for itm options
                    strike = atm_strike
                    symbol, symbol_token = self.kite_functions.get_options_symbol_and_token(underlying_name, atm_strike, 'PE')
                otm_strike = strike - starting_distance
                if str(int(otm_strike))[-2] == '5': #fix for itm strikes where atm strike is multiple of 50
                    otm_strike -= 50
                for _ in range(20):
                    nf_bnf_symbol_pe, bnf_token_ce = self.kite_functions.get_options_symbol_and_token(underlying_name, otm_strike, 'PE')
                    # If symbol is not present in instrument_df stop
                    if nf_bnf_symbol_pe == None:
                        break
                    #filter out 100, 400 and 900 strikes. idx is -5 because ends with PE
                    if not ((underlying_name == 'BANKNIFTY' or underlying_name == 'FINNIFTY') and str(otm_strike)[-5] in ['1', '4', '9']):
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
            logger.exception(f"Unexpected error while finding hedge for {symbol}. Error: "+str(e))
            telegram_bot_sendtext(f"Unexpected error while finding hedge for {symbol}. Error: "+str(e))
            traceback.print_exc()
            return None, None

    def get_running_pnl(self, given_time = None):
        try:
            current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            for strategy_name, strategy_orders_dict in self.trades_dict.items():
                pnl = 0
                qty = 0
                lot_pnl = 0
                legs_hit = 0

                if 'ce_details' in strategy_orders_dict:
                    order_lot_pnl = strategy_orders_dict['ce_details']['sell_price'] - strategy_orders_dict['ce_details']['buy_price']
                    lot_pnl = lot_pnl + order_lot_pnl
                    qty = strategy_orders_dict['ce_details']['qty']
                    pnl = pnl + (order_lot_pnl * qty)
                    if strategy_orders_dict['ce_details']['sl_hit']:
                        legs_hit = legs_hit + 1

                if 'pe_details' in strategy_orders_dict:
                    order_lot_pnl = strategy_orders_dict['pe_details']['sell_price'] - strategy_orders_dict['pe_details']['buy_price']
                    lot_pnl = lot_pnl + order_lot_pnl
                    qty = strategy_orders_dict['pe_details']['qty']
                    pnl = pnl + (order_lot_pnl * qty)
                    if strategy_orders_dict['pe_details']['sl_hit']:
                        legs_hit = legs_hit + 1

                trade_dict = {
                    'date':str(current_dt.date()),
                    'day': str(current_dt.strftime('%A')),
                    'strategy': strategy_name,
                    'qty': qty,
                    'pnl': pnl,
                    'lot_pnl': lot_pnl,
                    'legs_hit': legs_hit,
                }
            
                if given_time:
                    trade_dict['given_time'] = given_time
                    data = list(trade_dict.values())
                    self.wks_running_pnl.append_row(data)
                else:
                    data = list(trade_dict.values())
                    self.wks_pnl.append_row(data)
                    telegram_bot_sendtext(f"PNL of {strategy_name}: \npnl: {pnl}\nlegs hit: {legs_hit}")

        except Exception as e:
            logger.exception(f"Unexpected error while get_running_pnl. Error: "+str(e))
            telegram_bot_sendtext(f"Unexpected error while get_running_pnl. Error: "+str(e))
            traceback.print_exc()

    def main(self):
        current_dt = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
        use_mis_order = self.iso_week_day not in NRML_DAYS

        if current_dt.hour < 14 or (current_dt.hour == 14 and current_dt.minute < 54):
            self.short_options_on_trigger()

        if current_dt.hour < 15 or (current_dt.hour == 15 and current_dt.minute < 15):
            self.check_for_target_hits()

        #Add straddles and strangles to websocket so that orders are executed around 9:16:00
        if self.add_straddle_strangle_to_websocket and current_dt.hour == 9 and current_dt.minute >=15:
            self.add_straddle_strangle_to_websocket = False
            nifty_ltp = eval(self.redis.get(str(self.nifty_token)))
            nf_atm_strike = get_nifty_atm_strike(nifty_ltp)
            self.add_itm_strangle_to_websocket(atm_strike = nf_atm_strike, distance_from_atm = 100, index = 'NIFTY')
            banknifty_ltp = eval(self.redis.get(str(self.bank_nifty_token)))
            bnf_atm_strike = get_banknifty_atm_strike(banknifty_ltp)
            self.add_itm_strangle_to_websocket(bnf_atm_strike, 0, index = 'BANKNIFTY')

        # Check and place orders
        for trades_item in self.trades_list:
            execution_day_details = [execution_days for execution_days in trades_item['execution_days'] if execution_days['day'] == self.iso_week_day]
            if len(execution_day_details) > 0:
                execution_day_details = execution_day_details[0]
                strategy_name = trades_item['strategy_name']

                if strategy_name not in self.trades_placed and check_if_time_is_allowed(current_dt, trades_item['entry_time']):
                    self.trades_placed.append(strategy_name)
                    if trades_item['strategy_type'] == 'add_to_watchlist':
                        self.add_to_watchlist(trades_item, execution_day_details)
                    if trades_item['strategy_type'] == 'short_straddle':
                        self.short_straddle(trades_item, execution_day_details)
            
                if strategy_name in self.trades_placed and 'exit_time' in execution_day_details:
                    if strategy_name not in self.trades_exited and check_if_time_is_allowed(current_dt, execution_day_details['exit_time']):
                        self.trades_exited.append(strategy_name)
                        self.cancel_orders_and_exit_position(trades_item, execution_day_details, self.trades_dict[strategy_name])

        # Exit orders at day end
        if not self.exit_procedure_done and current_dt.hour == 15 and current_dt.minute >=19:
            self.exit_procedure_done = True
            print("Exiting all placed orders")

            for each_order in self.kite.orders():
                if each_order['order_id'] in self.sl_order_id_list:
                    if each_order['status'] == 'TRIGGER PENDING':
                        self.orders_obj.cancel_order(each_order['order_id'])

            # Exit all placed orders
            for trades_item in self.trades_list:
                execution_day_details = [execution_days for execution_days in trades_item['execution_days'] if execution_days['day'] == self.iso_week_day]
                if len(execution_day_details) > 0:
                    execution_day_details = execution_day_details[0]
                    strategy_name = trades_item['strategy_name']

                    if strategy_name not in self.trades_exited:
                        self.trades_exited.append(strategy_name)
                        self.cancel_orders_and_exit_position(trades_item, execution_day_details, self.trades_dict[strategy_name])

            # Exit all MIS orders including manually placed
            for each_pos in self.kite.positions()['day']:
                if each_pos['tradingsymbol'] in self.traded_symbols_list and each_pos['product'] == 'MIS' and each_pos['quantity'] != 0:
                    exit_quantity = abs(each_pos['quantity'])
                    exit_type = "sell" if each_pos['quantity'] > 0 else "buy"
                    if exit_quantity > 0:
                        self.orders_obj.place_market_order(symbol = each_pos['tradingsymbol'], buy_sell= exit_type, quantity=exit_quantity, use_limit_order = True, use_mis_order = use_mis_order)

        # Get running pnl
        if (current_dt.hour > 9 and current_dt.hour < 15) or (current_dt.hour == 15 and current_dt.minute < 15) or (current_dt.hour == 9 and current_dt.minute > 30):
            if current_dt.hour not in self.running_pnl_done:
                self.running_pnl_done[current_dt.hour] = []
            if current_dt.minute % 15 not in self.running_pnl_done[current_dt.hour]:
                self.get_running_pnl(f"{current_dt.hour} : {(current_dt.minute % 15) * 15}")

        # Exit hedges
        if len(self.hedges_dict.keys()) > 0:
            dt_now = datetime.datetime.now()
            time_difference = dt_now - self.last_orders_checked_dt
            if time_difference.seconds >= 6:
                self.last_orders_checked_dt = dt_now
                for each_order in self.kite.orders():
                    if each_order['order_id'] in self.hedges_dict.keys():
                        if each_order['status'] in ['COMPLETE', 'CANCELLED'] and each_order['order_id'] not in self.hedge_exit_sl_order_id_list:
                            #if each_order['filled_quantity'] == each_order['quantity']:
                            self.hedge_exit_sl_order_id_list.append(each_order['order_id'])
                            qty = each_order['quantity']
                            hedge_symbol = self.hedges_dict[each_order['order_id']]
                            self.orders_obj.place_market_order(symbol = hedge_symbol, buy_sell= 'sell', quantity=qty, use_limit_order = False, use_mis_order = use_mis_order)

        #close
