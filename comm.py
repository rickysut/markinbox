# Serial class

from __future__ import absolute_import

import codecs
from typing import Text
from dblogging import LOGGER
import os
import sys
import threading
import time
import serial
import binascii
import pty
import logging
from serial.tools.list_ports import comports
from serial.tools import hexlify_codec

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("comm")

class Comm(object):
    """\
    Serial Communication class.
    """

    def __init__(self, config):
        self.serial = serial.Serial()
        self.serial.port = config["port"]
        self.serial.baudrate = config["baudrate"]
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.xonxoff = False
        self.serial.timeout = 0
        self.recvData = b''

    def comclose(self):
        try:
            self.serial.close()
            
        except:
            logging.error("error close port ")
            raise

    def comopen(self):
        try:
            self.serial.open()
            
        except:
            #print("error open port ")
            logging.error("error open port ")
            raise 

    def readDoor(self):
        self.recvData = ""
        try:
            time.sleep(.100)
            dt = self.serial.read(3)
            self.recvData = dt
        except serial.SerialException:
            logging.error("error read door data ")
            raise

    def sendDoor(self, data):
        try:
            
            self.serial.write(data.encode('utf-8'))
        except:
            logging.error("error send door data")
            raise

    def checkDoor(self):
        try:
            if self.serial != None:
                data = "S"
                self.sendDoor(data)
                #time.sleep(.10)
                self.readDoor()
                
                #print(self.recvData)
                if self.recvData != "":
                    dt = self.recvData.decode("utf-8").split("\r\n")
                    #print(dt)
                    return dt[0]
        except:
            return ""

    def read(self):
        #print("--Read Data --")
        self.recvData = ""
        try:
            time.sleep(.1)
            dt = self.serial.read(self.serial.in_waiting or 1)
            self.recvData = binascii.hexlify(bytearray(dt))
        except serial.SerialException:
            logging.error("error read data ")
            raise
            
    def send(self, data):
        try:
            cmd_bytes = bytearray.fromhex(data)
            for cmd_byte in cmd_bytes:
                hex_byte = ("{0:02x}".format(cmd_byte))
                self.serial.write(bytearray.fromhex(hex_byte))
                #time.sleep(.1)
        except:
            logging.error("error send data")
            raise
    
    def _hexPacketNo(self, no):
        try:    
            #print("_hexPacketNo", no)
            pktno = no
            c1 = pktno//10
            c2 = pktno % 10
            return ("{0:x}".format(ord(str(c1)))) + ("{0:x}".format(ord(str(c2))))
        except:
            raise

    def convertHex(self, txt):
        result = ""
        for x in range(len(txt)):
            result = result + ("{0:x}".format(ord(txt[x])))
        return result


    def getStatus(self, packetno):
        try:
            #print(self.serial)
            if self.serial == None:
                #print("serial none")
                self.serial.comclose()
                self.serial.comopen()

            if self.serial != None:

                nomor = self._hexPacketNo(packetno)
                
                data = "4002"+nomor+"303530303003"
                #print(data)
                #print("senddata")
                self.send(data)
                #time.sleep(.10)
                #print("readdata")
                self.read()
                
                #print(str(self.recvData, 'UTF-8'))
                if self.recvData != "":
                    st = str(self.recvData, 'UTF-8')
                    #print(st)
                    i = st.find("4002"+nomor+"3036202032")
                    if i == 0 :
                        #400230303036202032203003
                        res=  st[18:22]
                        #print("Res: " , res)
                        if res == "3939": return "Alarm"
                        if res == "2030": return "Standby"
                        if res == "2031": return "Marking"
                        if res == "2032": return "Halting"
                        if res == "2033": return "Returning to origin"
                        if res == "2035": return "Other"

        except:
            #print("serial ", self.serial)
            return "Error"

    def sendLine(self, txt, packetno, fileno, lineno):
        try:
            '''Num of Char'''
            lt = len(txt)
            stCharLen = str(lt).zfill(2)
            #print(stCharLen)
            stHexCharLen = self.convertHex(stCharLen)
            #print("Char len:", stHexCharLen)

            '''data length'''
            datalen = 7 + lt
            stDataLen = str(datalen).zfill(3) #010 : 3 digit
            #print(stDataLen)
            stHexDataLen = self.convertHex(stDataLen)
            #print("data length:", stHexDataLen)

            '''File no'''
            stHexFile = self.convertHex(fileno)
            #print("File no:",stHexFile)

            '''Field No'''
            stLineNo = str(lineno).zfill(2)
            #print(stLineNo)
            stHexLineNo = self.convertHex(stLineNo)
            #print("Field no:",stHexLineNo)

            '''Paketno'''
            pkt = self._hexPacketNo(packetno)
            #print("Pkt no:", pkt)

            '''Text'''
            stHexText = self.convertHex(txt)
            #print("Txt:", stHexText)

            if self.serial != None:
                data = "4002"+pkt+"3039"+stHexDataLen+stHexFile+stHexLineNo+stHexCharLen+stHexText+"03"
                #print(data)
                self.send(data)
                self.read()
                if self.recvData != "":
                    st = str(self.recvData, 'UTF-8')
                    #print(st)
                    i = st.find("4002"+pkt+"31302020310603")
                    if i == 0:
                        #print("ACK")
                        return "ACK"
                    else:
                        return "NACK"
        except:
            return "Error"

    def commitMark(self, packetno, fileno):
        try:
            if self.serial != None:
                '''File no'''
                stHexFile = self.convertHex(fileno)
                #print("File no:", stHexFile)
                nomor = self._hexPacketNo(packetno)

                data = "4002"+nomor+"3131303033"+stHexFile+"03"
                #print(data)
                self.send(data)
                #time.sleep(.10)
                self.read()

                #print(str(self.recvData, 'UTF-8'))
                if self.recvData != "":
                    st = str(self.recvData, 'UTF-8')
                    #print(st)
                    i = st.find("4002"+nomor+"31322020310603")
                    if i == 0:
                        
                        return "ACK"
                    else:
                        return "NACK"

        except:
            return "Error"
