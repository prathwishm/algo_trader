from math import modf
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('convert_float_to_tick_price.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(file_handler)

def convert_to_tick_price(price_inp):
    # Convert price to end with .x0 or .x5 where "x" is any number between 0-9
    try:
        # frac, whole = modf(price_inp) #modf faction part is ambiguous and has a lot of digits instead of 2
        # frac += 0.0001 #fix for decimals having less than 3 digits
        # if int(str(frac)[3]) in range(7,10):
        #     second_digit = 0
        #     first_digit = int(str(frac)[2]) +1
        # elif int(str(frac)[3]) in range(3,7):
        #     second_digit = 5
        #     first_digit = int(str(frac)[2])
        # else:
        #     second_digit = 0
        #     first_digit = int(str(frac)[2])
        # return round(whole + first_digit/10 + second_digit/100, 2)
        return round(price_inp, 1)
    
    except Exception as e:
        logger.exception('Error while converting float to tick')
        return round(price_inp, 1)