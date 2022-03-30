#import base64
#import hashlib
from cryptography.fernet import Fernet
#from Cryptodome.Cipher import AES as domeAES
#from Cryptodome.Random import get_random_bytes
#from Crypto import Random
#from Crypto.Cipher import AES as cryptoAES
#import binascii

#BLOCK_SIZE = cryptoAES.block_size

key = "qBq3m8sFvKbaFkTnvqcDdcdv_YwsWUSi6gFwQ1vtB28="




def encryptDecrypt(txt):
    xorKey = '^'
    res = ''

    ilen = len(txt)

    for i in range(ilen):
        res += chr(ord(txt[i]) ^ ord(xorKey))
    return res

def encrypt(txt):
    f = Fernet(key)
    enc = encryptDecrypt(txt)
    b = f.encrypt(enc.encode()).decode()
    return b


def decrypt(txt):
    f = Fernet(key)
    dec = f.decrypt(txt)
    b = encryptDecrypt(dec.decode())
    return b

