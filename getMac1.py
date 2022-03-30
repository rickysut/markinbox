from getmac import get_mac_address
from cryptography.fernet import Fernet
import binascii 


eth_mac = get_mac_address(interface="en0")
print(eth_mac)



def encryptDecrypt(txt): 
    xorKey = '^'
    res = ''
    

    ilen = len(txt)

    for i in range (ilen):
        res += chr(ord(txt[i]) ^ ord(xorKey)).upper()
    return res


xstr = encryptDecrypt(eth_mac)
print(xstr)
dstr = encryptDecrypt(xstr.lower())
print(dstr)

key = 'qBq3m8sFvKbaFkTnvqcDdcdv_YwsWUSi6gFwQ1vtB28='
f = Fernet(key)
password = f.encrypt(dstr.lower().encode()).decode()
print(password)

coba = 'gAAAAABhXblTlLNW-c0_cmU5rsiyp76AdqewdxogRMtn-DdNc_XBPMAR-ImhMTyreM02u2sT9Hq3l02wbR9Scv7e5eBlvPzozrjhM5KQ3h1kduCi4JYgt6M='
passwd = f.decrypt(coba.encode()).decode()
print(passwd)

