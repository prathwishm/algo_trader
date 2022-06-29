from kiteext import KiteExt
from kiteconnect import KiteTicker
import urllib.parse
import requests

class KiteExt_new(KiteExt):
    def login_using_enctoken(self, userid, enctoken, public_token):
        self.headers = {
            'x-kite-version': '3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
        }
        self.user_id = userid
        self.reqsession = requests.Session()

        self.enctoken = enctoken
        self.public_token = public_token
        #self.user_id = r.cookies.get('user_id')

        self.headers['Authorization'] = 'enctoken {}'.format(self.enctoken)

    def kws(self, api_key='kitefront'):
        return KiteTicker(api_key=api_key, access_token='&user_id='+self.user_id+'&enctoken='+urllib.parse.quote(self.enctoken), root='wss://ws.zerodha.com')

    def ticker(self, api_key='kitefront', enctoken=None, userid=None):
        if enctoken is not None:
            self.enctoken = enctoken
        if userid is not None:
            self.user_id = userid
        if self.user_id is None:
            raise Exception(
                f'userid cannot be none, either login with credentials first or set userid here')
        return KiteTicker(api_key=api_key, access_token='&user_id='+self.user_id+'&enctoken='+urllib.parse.quote(self.enctoken), root='wss://ws.zerodha.com')