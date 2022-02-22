from kiteext import KiteExt
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