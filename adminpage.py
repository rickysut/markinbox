""" adminpage.py - Copyright Ricky sutanto """

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog)

import resource
import dbconn
import logging
import mainpage

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("adminpage")


class adminWindow(QDialog):
    def __init__(self, userdata):
        super(adminWindow, self).__init__()
        self.userData = userdata

    def _show(self):
        loadUi("Admin.ui", self)
        if (self.userData.get('user_role') == 1): #operator & spv
            #print("not admin")
            self.butPartNumber.hide()
        mainpage.mainWindow.adminMenu = 0
        self.butPartNumber.clicked.connect(self.handlePartClick)
        self.butUser.clicked.connect(self.handleUserClick)
        
    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            event.accept()
            
    def closewin(self):
        self.close()

    def handlePartClick(self):
        mainpage.mainWindow.adminMenu = 1
        self.closewin()

    def handleUserClick(self):
        mainpage.mainWindow.adminMenu = 2
        self.closewin()
