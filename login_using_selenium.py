import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
import time
from telegram_bot import telegram_bot_sendtext
from config import kite_username, kite_password, kite_pin

def login_using_selenium():
    try:
        s=Service(ChromeDriverManager().install())
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=s, options=options)
        driver.get('https://kite.zerodha.com/')
        driver.implicitly_wait(25)
        time.sleep(5)

        #Find User ID and Password input
        username = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[2]/input')
        password = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[3]/input')

        #Type User ID and Passwod
        username.send_keys(kite_username)
        password.send_keys(kite_password)

        #click on Login
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[4]/button').click()

        time.sleep(5)
        #Find input to enter Pin
        pin = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[2]/div/input')

        #Type the Pin
        pin.send_keys(kite_pin)

        #Click on Continue
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[3]/button').click()

        #Store the Cookies and enctoken
        time.sleep(3)
        cookie = driver.get_cookies()

        for idx, each_dict in enumerate(cookie):
            if each_dict['name'] == 'public_token':
                cookie[idx]['domain'] = 'kite.zerodha.com'  # 'kite' is added to Domain for login on web browser
            if each_dict['name'] == 'enctoken':
                with open('enctoken.txt', 'w+') as wr:
                    wr.write(each_dict['value'])
                print("Enctoken Updated")

        driver.quit()
        #telegram_bot_sendtext('Kite web login cookies are')
        telegram_bot_sendtext('[' + str(json.dumps(cookie)) + ']', filter_text=False)
        return True

    except Exception as e:
        telegram_bot_sendtext("Error while logging in using Selenium. Error: "+str(e))
        print("Error while logging in using Selenium. Error: "+str(e))
        traceback.print_exc()
        return False

if __name__ == '__main__':
    login_using_selenium()