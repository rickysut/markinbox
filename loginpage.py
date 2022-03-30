""" loginpage.py - Copyright Ricky sutanto """




from array import array
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QDesktopWidget, QLineEdit)

import dbconn
import logging
import mainpage
import json
import encdec
import dblogging
import datetime

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("loginpage")


class loginScreen(QDialog):

    def __init__(self):
        super(loginScreen, self).__init__()
        

    def setWidget(self, stackedWidget):
        self.widget = stackedWidget
        loadUi("loginScreen.ui", self)
        self.le_password.setEchoMode(QLineEdit.Password)
        self.loginButton.clicked.connect(self.LoginNow)
        self.cancelButton.clicked.connect(self.cancelLogin)
        

    def LoginNow(self):
        self.deleteAllWidget()
        uid = self.le_userId.text()
        upwd = self.le_password.text()
        ''' check db here '''
        with open("config.json") as json_data_file:
            data = json.load(json_data_file)
        #print(data["db"]["password"])
        pwd = data["db"]["password"]
        ori = encdec.decrypt(pwd.encode())
        #print(ori)
        data["db"]["password"] = ori

        conn_pool = dbconn.mysql_db(data["db"], time_to_sleep=5, test_run=True)
        pool = conn_pool.get_initialized_connection_pool()
        assert pool.qsize() == 20
        
        cursor = conn_pool.get_connection().cursor()
        dblog = dblogging.dbLogging(conn_pool)

        with cursor:
            sql = "SELECT user_id, user_login, user_name, AES_DECRYPT(unhex(user_pwd), SHA2('S4tu1tu3s4',256)) as user_pwd ,user_status, user_role from `mk_users` where UPPER(user_login)=UPPER(%s) and user_status = 1"
            cursor.execute(sql, (uid))
            result = cursor.fetchone()
            if (result == None):
                self.errLabel.setText("Invalid User ID")
                self.le_userId.setFocus()
                self.le_userId.selectAll()
                
                wuid = -1
                hist = [wuid, "AUTH", "LOG-IN", "Invalid User ID: " + uid, ""]
                dblog.writeHistory(hist)
            else:
                #print(result)
                if (result.get("user_pwd").decode("UTF-8") == upwd):
                    uid = result.get("user_id")
                    uName = result.get("user_name")
                    self.errLabel.setText("")
                    self.le_password.setText("")
                    self.le_password.setFocus()
                    self.le_password.selectAll()
                    main = mainpage.mainWindow(result)
                    main._show(self.widget)
                    main._setdbconn(conn_pool)
                    self.widget.setGeometry(0, 0, main.width(),main.height())
                    self.widget.setFixedSize(main.width(), main.height())
                    self.widget.setWindowTitle("MAINPAGE")
                    size = main.size()
                    desktopSize = QDesktopWidget().screenGeometry()
                    top = (desktopSize.height()/2)-(size.height()/2)
                    left = (desktopSize.width()/2)-(size.width()/2)
                    self.widget.move(int(left), int(top))
                    if self.widget.indexOf(main) == -1:
                        self.widget.addWidget(main)
                    
                    self.widget.setCurrentIndex(self.widget.currentIndex()+1)
                    
                    
                    hist = [uid, "AUTH", "LOG-IN", "Valid user id & password", uName]
                    dblog.writeHistory(hist)
                else:
                    self.errLabel.setText("Invalid Password!")
                    self.le_password.setFocus()
                    self.le_password.selectAll()
                    
                    uid = result.get("user_id")
                    hist = [uid, "AUTH", "LOG-IN", "Invalid password", ""]
                    dblog.writeHistory(hist)

    def cancelLogin(self):
        self.widget.close()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.widget.close()
        elif event.key() == Qt.Key_Return:
            event.accept()
            self.LoginNow()

    def deleteAllWidget(self):
        #first check whether the layout we want to delete exists
        thisItem = self.widget.currentWidget()
        #print(thisItem)
        if self.widget.count() > 1:
            #delete each widget in the layout one by one
            while self.widget.count() > 1:
                for x in range(self.widget.count()):
                    item = self.widget.widget(x)
                    #print(item)
                    if (item is not None) and (item is not thisItem):
                        self.widget.removeWidget(item)
                        break
                    else:
                        continue
        else:
            pass
