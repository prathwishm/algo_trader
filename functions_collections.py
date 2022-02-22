import pandas as pd
import pandas_ta as ta
import talib
import datetime
from dateutil.tz import tzoffset
import time

class Kite_functions():

    def __init__(self, kite):
        self.kite = kite
        self.instrument_df = pd.DataFrame(kite.instruments())
    
    def get_order_list(self):
        #time.sleep(0.2)
        order_list = []
        for try_no in range(10):
            try:
                order_list = self.kite.orders()
                break
            except Exception as e:
                print("can't get orders..retrying")
                if try_no == 9:
                    print("Could not fetch orders. Error: "+str(e))
        return order_list

    def get_positions_list(self, sleep = False):
        if sleep:
            time.sleep(0.2)
        positions_list = []
        for try_no in range(10):
            try:
                positions_list = self.kite.positions()
                break
            except Exception as e:
                print("can't get positions..retrying")
                if try_no == 9:
                    print("Could not fetch positions. Error: "+str(e))
        return positions_list

    def get_symbol_token(self,symbol):
        """Looks up instrument token for a given script from instrument dump"""
        try:
            if symbol[0:4] == 'NSE:':
                symbol = symbol[4:]
            return self.instrument_df[self.instrument_df.tradingsymbol==symbol].instrument_token.values[0]
        except Exception as e:
            print(f"Error while getting token for {symbol}. Error: {e}")
            return -1

    def get_trading_symbol_from_token(self, token):
        """Looks up instrument symbol for a given script from instrument dump"""
        try:
            return self.instrument_df[self.instrument_df.instrument_token==token].tradingsymbol.values[0]
        except:
            return -1

    @staticmethod
    def get_vwap(df_in):
        df = df_in.copy()
        current_date = df.index[0].date()
        start_idx = df.index[0]
        vwap = pd.Series()
        for idx, row in df.iterrows():
            if idx.date() != current_date:
                temp_df = df.loc[start_idx:prev_idx]
                vwap = vwap.append(ta.vwap(temp_df['high'], temp_df['low'], temp_df['close'], temp_df['volume']))
                current_date = idx.date()
                start_idx = idx
            prev_idx = idx
        temp_df = df.loc[start_idx:]
        vwap = vwap.append(ta.vwap(temp_df['high'], temp_df['low'], temp_df['close'], temp_df['volume']))
        return vwap


    def data_downloader(self, name, interval, delta):
        #token = self.kite.ltp(name)[name]['instrument_token']
        token = self.get_symbol_token(name)
        to_date = datetime.datetime.now().date()
        from_date = to_date - datetime.timedelta(days = delta)
        data = self.kite.historical_data(instrument_token = token , from_date = from_date, to_date = to_date, interval = interval , continuous=False, oi=False)
        df = pd.DataFrame(data)
        df.set_index("date", inplace = True)
        return df


    def add_indicators(self, df):
        df['vwap'] = self.get_vwap(df)
        df["upperband"], df["middleband"], df["lowerband"] = talib.BBANDS(df["close"], timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)
        df['bb_width_percent'] = (df["upperband"] - df["lowerband"])/ df['close']
        df['10sma_vol'] = talib.SMA(df['volume'], timeperiod=10)
        df['240sma'] = talib.SMA(df['close'], timeperiod=240)
        df.dropna(inplace=True)
        return df

    @staticmethod
    def convert_tick_data_to_candles(tick_data = [], time_frame='5min'):
        df = pd.DataFrame(tick_data, columns=['date','ltp', 'abs_volume'])
        df.set_index(['date'], inplace=True)
        df.index = pd.to_datetime(df.index)
        df_ohlc = df['ltp'].resample(time_frame).ohlc().dropna()
        df_ohlc['vol'] = df['abs_volume'].resample(time_frame).max().dropna()
        df_ohlc['volume'] = df_ohlc.vol.diff()
        if df_ohlc.index[0].minute == 15 and df_ohlc.index[0].hour == 9:
            df_ohlc.loc[df_ohlc.index[0], 'volume'] = df_ohlc.loc[df_ohlc.index[0], 'vol']
        df_ohlc.dropna(inplace=True)
        df_ohlc.drop('vol', axis=1, inplace=True)
        df_ohlc.index = df_ohlc.index.tz_localize(tz=tzoffset(None, 19800))
        return df_ohlc

    def add_five_min_bb_bull_blast_indicators(self, df):
        df['vwap'] = self.get_vwap(df)
        df["upperband"], df["middleband"], df["lowerband"] = talib.BBANDS(df["close"], timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)
        df['20sma_vol'] = talib.SMA(df['volume'], timeperiod=20)
        df['200sma'] = talib.SMA(df['close'], timeperiod=200)
        df.dropna(inplace=True)
        return df

    def get_options_symbol_and_token(self, name, strike, ce_pe):
        inst = self.instrument_df
        temp = inst[inst['exchange'] == 'NFO']
        temp = temp[temp['segment'] == 'NFO-OPT']
        temp = temp[temp['name'] == name]
        expiry = sorted(list(temp[temp['exchange'] == 'NFO']['expiry'].unique()))[0]
        #print(expiry)
        temp = temp[temp['expiry'] == expiry]
        temp = temp[temp['strike'] == strike]
        temp = temp[temp['instrument_type'] == ce_pe]
        return list(temp['tradingsymbol'])[0], list(temp['instrument_token'])[0]

    def get_futures_symbol_and_token(self, name):
        inst = self.instrument_df
        temp = inst[inst['exchange'] == 'NFO']
        temp = temp[temp['segment'] == 'NFO-FUT']
        temp = temp[temp['name'] == name]
        expiry = sorted(list(temp[temp['exchange'] == 'NFO']['expiry'].unique()))[0]
        #print(expiry)
        temp = temp[temp['expiry'] == expiry]
        return list(temp['tradingsymbol'])[0], list(temp['instrument_token'])[0]