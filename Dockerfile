FROM python:3.9

# # Adding trusting keys to apt for repositories
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# # Adding Google Chrome to the repositories
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# # Updating apt to see and install Google Chrome
# RUN apt-get -y update

# # Magic happens
# RUN apt-get install -y google-chrome-stable

# # Installing Unzip
# RUN apt-get install -yqq unzip

# # Download the Chrome Driver
# RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/100.0.4896.20/chromedriver_linux64.zip

# # Unzip the Chrome Driver into /usr/local/bin directory
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# # Set display port as an environment variable
# ENV DISPLAY=:99

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
ADD config.py .
ADD convert_float_to_tick_price.py .
ADD credentials.txt .
ADD enctoken.txt .
ADD functions_collections.py .
ADD kite_ext_new.py .
ADD login_using_selenium.py .
ADD main_.py .
ADD orders.py .
ADD straddle_strategy2.py .
ADD telegram_bot.py .
ADD telegram_bot_credentials.txt .
ADD ticker_service.py .
ADD update_ticks_using_celery.py .
CMD ["python", "./main_.py"]
