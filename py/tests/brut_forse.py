import requests

alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
test = [1, 2, 3, 4]

base = len(alphabet)

n = 0
length = 1

print('Start brut force')
while n != 10000:
    temp_n = n
    password = ''
    while temp_n > 0:
        k = temp_n // base
        rest = temp_n % base
        password = alphabet[rest] + password
        temp_n = k

    while len(password) < length:
        password = alphabet[0] + password

    if alphabet[-1] * length == password:
        length += 1
        n = 0
    else:
        n += 1
    print(password)
