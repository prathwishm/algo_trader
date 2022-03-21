import requests
from urllib.parse import quote
from threading import Thread

with open('telegram_bot_credentials.txt', 'r') as credentials:
    lines = credentials.readlines()
    bot_token = str(lines[0]).strip()
    bot_chatID = str(lines[1]).strip()
    #print(bot_token, bot_chatID)


def telegram_bot_sendtext_main(bot_message_in):
    try:
        #bot_message = bot_message_in.replace("&", " ").replace("_", " ").replace("@", " ").replace("'", " ").replace("[", " ")
        bot_message = quote(str(bot_message_in))
        if len(bot_message) > 4096:
            n = int(len(bot_message) / 4096)
            for i in range(n+1):
                if i == n:
                    message = bot_message[i*4096:]
                else:
                    message = bot_message[i*4096:(i+1)*4096]
                send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + message
                response = requests.get(send_text)
        else:
            send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
            response = requests.get(send_text)

        return response.json()
    except Exception as e:
        print("Error while Sending telegram message. Error: "+str(e))
        return None

def telegram_bot_sendtext(bot_message_in, filter_text = True):
    if filter_text:
        bot_message_in = bot_message_in.replace("&", " ").replace("_", " ").replace("@", " ")
    x = Thread(target = telegram_bot_sendtext_main, args = [bot_message_in])
    x.start()

if __name__ == "__main__":
    test = telegram_bot_sendtext("Testing the telegram bot...")
    print(test)
