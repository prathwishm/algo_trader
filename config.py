
with open('credentials.txt', 'r') as credentials:
    lines = credentials.readlines()
    kite_username = lines[0].replace('\n','')
    kite_password = lines[1].replace('\n','')
    kite_pin = lines[2].replace('\n','')
