
with open('credentials.txt', 'r') as credentials:
    lines = credentials.readlines()
    kite_username = lines[0]
    kite_password = lines[1]
    kite_pin = lines[2]
