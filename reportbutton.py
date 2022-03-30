""" reportbutton.py - Copyright Ricky sutanto """

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog)

import resource
import dbconn
import logging
import mainpage

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("reportbutton")


class reportButton(QDialog):
    def __init__(self, userdata):
        super(reportButton, self).__init__()

        self.userData = userdata
        

    def _show(self):
        loadUi("reportbut.ui", self)
        mainpage.mainWindow.reportMenu = 0
        self.butReport.clicked.connect(self.handleReportClick)
        self.butBackup.clicked.connect(self.handleBackupClick)
        self.butProduction.clicked.connect(self.handleProductionClick)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            event.accept()

    def closewin(self):
        self.close()

    def handleReportClick(self):
        mainpage.mainWindow.reportMenu = 1
        self.closewin()

    def handleBackupClick(self):
        mainpage.mainWindow.reportMenu = 2
        self.closewin()

    def handleProductionClick(self):
        mainpage.mainWindow.reportMenu = 3
        self.closewin()
