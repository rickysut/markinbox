""" mainpage.py - Copyright Ricky sutanto """


import sys

import pymysql as db

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDesktopWidget, QMainWindow, QMessageBox)


import resource
import logging
import loginpage
import markpage
import dblogging
import adminpage
import userpage
import partpage
import reportbutton
import backuppage
import reportpage
import production


logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("mainpage")


class mainWindow(QMainWindow):
    adminMenu = -1
    reportMenu = -1
    def __init__(self, userdata):
        super(mainWindow, self).__init__()
        self.userData = userdata
        self.userRole = userdata.get("user_role")

    def _setdbconn(self, conn):
        self.conn = conn
        self.username = self.userData.get("user_name")
        self.dblog = dblogging.dbLogging(self.conn)


    def _show(self, stackedWidget):
        loadUi("mainwindow.ui", self)
        self.widget = stackedWidget
        #self.showMaximized()
        #desktopSize = QDesktopWidget().screenGeometry()
        #self.setFixedSize(desktopSize.width(), desktopSize.height())
        self.butExit.clicked.connect(self.closewin)
        self.butMark.clicked.connect(self.markinScreen)
        self.butAdmin.clicked.connect(self.adminScreen)
        if int(self.userRole) > 2:
            self.butReportBackup.setEnabled(True)
            self.butReportBackup.clicked.connect(self.backupBut)
        else:
            self.butReportBackup.setEnabled(False) 

    def closewin(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Logout ?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if msgBox.exec_() == QMessageBox.Yes:
            page = loginpage.loginScreen()
            page.setWidget(self.widget)
            self.widget.setCurrentIndex(self.widget.currentIndex()-1)
            self.widget.setGeometry(0, 0, page.width(), page.height())
            self.widget.setFixedSize(page.width(), page.height())
            self.widget.setWindowTitle("LOGIN")
            size = page.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)
            self.widget.move(left, top)
            userid = self.userData.get("user_id")
            hist = [userid, "MAINPAGE", "LOG-OUT", "", self.username]
            self.dblog.writeHistory(hist)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            event.ignore()

    def markinScreen(self):
        self.deleteAllWidget()
        markScreen = markpage.markWindow(self.userData)
        markScreen._show(self.widget)
        markScreen._setdbconn(self.conn)
        self.widget.setGeometry(0, 0, markScreen.width(), markScreen.height())
        self.widget.setFixedSize(markScreen.width(), markScreen.height())
        size = markScreen.size()
        desktopSize = QDesktopWidget().screenGeometry()
        top = (desktopSize.height()/2)-(size.height()/2)
        left = (desktopSize.width()/2)-(size.width()/2)
        #self.widget.setFixedSize(desktopSize.width(), desktopSize.height())
        self.widget.move(int(left), int(top))
        if self.widget.indexOf(markScreen) == -1:
            self.widget.addWidget(markScreen)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1)
        self.widget.setWindowTitle("MARKING PAGE")
        userid = self.userData.get("user_id")
        #print("user id", userid)
        hist = [userid, "MAINPAGE", "MARKING", "", self.username]
        self.dblog.writeHistory(hist)
        #print("-- Open Port --")
        markScreen._openComPort()
        markScreen._openDoorPort()

    def adminScreen(self):
        
        adminScreen = adminpage.adminWindow(self.userData)
        adminScreen._show()
        size = adminScreen.size()
        desktopSize = QDesktopWidget().screenGeometry()
        top = (desktopSize.height()/2)-(size.height()/2)
        left = (desktopSize.width()/2)-(size.width()/2)
        adminScreen.move(left, top)
        adminScreen.exec()
        if self.adminMenu == 1: #part number DB
            repScreen = partpage.partWindow(self.userData)
            repScreen._show(self.conn)
            size = repScreen.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)
            repScreen.move(left, top)
            repScreen.exec()
        elif self.adminMenu == 2:  # part number DB
            userScreen = userpage.userWindow(self.userData)
            userScreen._show(self.conn)
            size = userScreen.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)
            userScreen.move(left, top)
            userScreen.exec()

    def deleteAllWidget(self):
        #first check whether the layout we want to delete exists
        thisItem = self.widget.currentWidget()
        idx = self.widget.currentIndex()
        #print(thisItem)
        if self.widget.count() > 1:
            #delete each widget in the layout one by one
            
            for x in range(idx, self.widget.count()):
                item = self.widget.widget(x)
                #print("-->",item)
                if (item is not None) and (item is not thisItem):
                    self.widget.removeWidget(item)
                
        else:
            pass

    def backupBut(self):
        reportBut = reportbutton.reportButton(self.userData)
        reportBut._show()
        size = reportBut.size()
        desktopSize = QDesktopWidget().screenGeometry()
        top = (desktopSize.height()/2)-(size.height()/2)
        left = (desktopSize.width()/2)-(size.width()/2)
        reportBut.move(left, top)
        reportBut.exec()
        if self.reportMenu == 1:  # reporting
            print("reporting")
            repScreen = reportpage.reportWindow(self.userData)
            repScreen._show(self.conn)
            size = repScreen.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)
            repScreen.move(left, top)
            repScreen.exec()
        if self.reportMenu == 2:  # part number DB
            bckScreen = backuppage.backupWindow(self.userData)
            bckScreen._show(self.conn)
            size = bckScreen.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)
            bckScreen.move(left, top)
            bckScreen.exec()
        if self.reportMenu == 3:  # Production
            prdScreen = production.Production(self.userData)
            prdScreen._show(self.conn)
            size = prdScreen.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)
            prdScreen.move(left, top)
            prdScreen.exec()
            

        
        
       

