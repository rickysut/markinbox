import time
import binascii
import serial
import sys
import os


def mulai():
    ser = serial.Serial('/dev/tty.usbserial-14310', 115200,
                        parity=serial.PARITY_NONE, timeout=0)
    data = '40023030303530303003'
    #test = bytearray([0x40, 0x02, 0x30, 0x30, 0x30,
                     #0x35, 0x30, 0x30, 0x30, 0x03])
    #ser.write(test)
    cmd_bytes = bytearray.fromhex(data)
    #print(cmd_bytes)
    #ser.write(cmd_bytes)
    for cmd_byte in cmd_bytes:
        hex_byte = ("{0:02x}".format(cmd_byte))
        #print(hex_byte)
        ser.write(bytearray.fromhex(hex_byte))
        time.sleep(.1)

    time.sleep(.10)
    out = ser.read(ser.in_waiting or 1)
    datanya = binascii.hexlify(bytearray(out))
    ser.close()
    print(str(datanya, 'UTF-8'))


if __name__ == "__main__":
    mulai()
