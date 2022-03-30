import base64
import hashlib
from Cryptodome.Cipher import AES as domeAES
from Cryptodome.Random import get_random_bytes
from Crypto import Random
from Crypto.Cipher import AES as cryptoAES
import binascii
from ast import literal_eval

BLOCK_SIZE = cryptoAES.block_size

key = "S4tu1tu3s4".encode()

__key__ = hashlib.sha256(key).digest()
#ckey = binascii.hexlify(__key__)
#__key__ = "a217ef66a8042d09923e3f954c6b19e4246c47bfd3470e0d76b03900dc23aad3"
#print(__key__)
#sdx = binascii.hexlify(__key__).decode('ascii')
#print(sdx)



def encrypt(raw):
    BS = cryptoAES.block_size
    def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    raw = base64.b64encode(pad(raw).encode('utf8'))
    iv = get_random_bytes(cryptoAES.block_size)
    cipher = cryptoAES.new(key=__key__, mode=cryptoAES.MODE_CFB, iv=iv)
    a = base64.b64encode(iv + cipher.encrypt(raw))
    IV = Random.new().read(BLOCK_SIZE)
    aes = domeAES.new(__key__, domeAES.MODE_CFB, IV)
    b = base64.b64encode(IV + aes.encrypt(a))
    return b


def decrypt(enc):
    passphrase = __key__
    encrypted = base64.b64decode(enc)
    IV = encrypted[:BLOCK_SIZE]
    aes = domeAES.new(passphrase, domeAES.MODE_CFB, IV)
    enc = aes.decrypt(encrypted[BLOCK_SIZE:])
    def unpad(s): return s[:-ord(s[-1:])]
    enc = base64.b64decode(enc)
    iv = enc[:cryptoAES.block_size]
    cipher = cryptoAES.new(__key__, cryptoAES.MODE_CFB, iv)
    b = unpad(base64.b64decode(cipher.decrypt(
        enc[cryptoAES.block_size:])).decode('utf8'))
    return b


encrypted_data = encrypt("root")
print("1:",encrypted_data)
save = encrypted_data.decode()
print("save:", save)

mms = save.encode()
#print(binascii.hexlify(encrypted_data))
print("2:",mms)

#data = encrypted_data.hex()
#print("3:",data)

#ori = bytes(mms.decode(), 'utf-8')
#print("4:", ori)


decrypted_data = decrypt(mms)
print("5:",decrypted_data)
