""" markinbox.py - Copyright Ricky sutanto """



import sys
import os
import hashlib
import pymysql as db
import psutil

from PyQt5 import QtGui
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QMessageBox, QInputDialog)
from cryptography.fernet import Fernet
from getmac import get_mac_address

import json
import logging
import loginpage
#from Crypto.Cipher import AES



logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("markinbox")



class MarkinBox(QtWidgets.QStackedWidget):
    
    entryKey = ""
    instan = 0
    def __init__(self, parent=None):
        super(MarkinBox, self).__init__(parent=parent)
   
    def encryptDecrypt(self, txt):
        xorKey = '^'
        res = ''

        ilen = len(txt)

        for i in range(ilen):
            res += chr(ord(txt[i]) ^ ord(xorKey)).upper()
        return res


    def _show(self, _widget):
        go = False
        key = 'qBq3m8sFvKbaFkTnvqcDdcdv_YwsWUSi6gFwQ1vtB28='
        f = Fernet(key)
        eth_mac = ""
        with open("config.json") as json_data_file:
            data = json.load(json_data_file)

        try:
            stPassKey = data["device"]["hash"]
            go = True
        except KeyError:
            pass

        #print(stPassKey)
        if (go == False):
            if os.name == 'nt':
                eth_mac = get_mac_address(interface="Ethernet")
            else:
                eth_mac = get_mac_address(interface="en0")
            #print(eth_mac)
            xstr = self.encryptDecrypt(eth_mac)
            text, ok = QInputDialog.getText(
                self, 'Key not Found', 'Enter key for id: %s' %(xstr))
            if ok:
                self.entryKey = str(text)
                entry = {'hash': self.entryKey}
                with open("config.json", "r+") as file:
                    data = json.load(file)
                    data['device'] = {'hash': self.entryKey}
                    file.seek(0)
                    json.dump(data, file)
            
            exit()

        keynya = f.decrypt(stPassKey.encode()).decode()
        #print("KEY = ", keynya)
        
        if os.name == 'nt':
            eth_mac = get_mac_address(interface="Ethernet")
        else:
            eth_mac = get_mac_address(interface="en0")
        #print(mac)
        if keynya == eth_mac:
            loginPage = loginpage.loginScreen()
            loginPage.setWidget(self)
            self.setGeometry(0, 0, loginPage.width(), loginPage.height())
            self.setFixedSize(loginPage.width(), loginPage.height())
            self.setWindowTitle("LOGIN")
            size = self.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)
            self.move(int(left), int(top))
            self.addWidget(loginPage)
            self.show()
        else:
            self.showMessage("Invalid hash key!")
        
            

    def closeEvent(self, event):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Quit Application?")
        msgBox.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if msgBox.exec_() == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def showMessage(self, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()
        
    def checkIfProcessRunning(self, processName):
        '''
        Check if there is any running process that contains the given name processName.
        '''
        #Iterate over the all the running process
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                
                # Check if process name contains the given name string.
                if processName.lower() in proc.name().lower():
                    #print(proc.name().lower(), proc.info)
                    self.instan += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return self.instan;


# Main


    
# Check if any chrome process was running or not.



app = QApplication(sys.argv)
widget =  MarkinBox()
if widget.checkIfProcessRunning("markinbox.exe") > 2:
    print("already running")
    sys.exit(1)
widget.setWindowIcon(QtGui.QIcon('marking.ico'))
widget.setWindowTitle("Markinbox-1.0")
widget._show(widget)


try:
    
    sys.exit(app.exec_())
except:
  
    print("Good Bye..")
