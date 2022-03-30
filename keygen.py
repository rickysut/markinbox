#CreateCred.py
#Creates a credential file.
from cryptography.fernet import Fernet

def encryptDecrypt(txt):
    xorKey = '^'
    res = ''

    ilen = len(txt)

    for i in range(ilen):
        res += chr(ord(txt[i]) ^ ord(xorKey))
    return res


def main():

	
	kode = input("kode: ")
	mac_asli = dstr = encryptDecrypt(kode)

	key = 'qBq3m8sFvKbaFkTnvqcDdcdv_YwsWUSi6gFwQ1vtB28='


	f = Fernet(key)
	#print("encode ", mac_asli.encode())
	keynya = f.encrypt(mac_asli.encode()).decode()
	print("KEY = ", keynya)
	#dec = f.decrypt(keynya.encode())
	#print("decrypt = ", dec)
	#print("result = ", encryptDecrypt(dec.decode()))

	


if __name__ == "__main__":
	main()
