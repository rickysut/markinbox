""" backuppage.py - Copyright Ricky sutanto """


from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QFileSystemModel, QDialog, QMessageBox, QLineEdit, QTextEdit, QLabel, QAbstractItemView, QTableWidgetItem)

import resource
import dbconn
import logging
import mainpage
import dblogging
import json
import os
import time
import datetime
import pipes
import encdec

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("backuppage")


class backupWindow(QDialog):
    def __init__(self, userdata):
        super(backupWindow, self).__init__()
        self.userData = userdata
        self.userId = userdata.get("user_id")
        with open("config.json") as json_data_file:
            data = json.load(json_data_file)
        self.comConfig = data["BACKUP"]
        self.configDB = data["db"]
        self.bakPath = self.comConfig["path"]
        self.bakPrefix = self.comConfig["prefix"]

    def _show(self, conn):
        loadUi("backup.ui", self)
        self.conn = conn
        self.dblog = dblogging.dbLogging(self.conn)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.btBackup.clicked.connect(self.doBackup)
        self.btCancel.clicked.connect(self.closewin)
        self.showList()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            event.accept()

    def showList(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(self.bakPath)
        
        
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(self.bakPath))
        self.treeView.setColumnWidth(0, 250)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.sortByColumn(3, Qt.DescendingOrder)

    def closewin(self):
        self.close()

    def showMessage(self, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()

    def doBackup(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Backup Database?")
        msgBox.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if msgBox.exec_() == QMessageBox.Yes:
            try:
                os.stat(self.comConfig["path"])
            except:
                os.mkdir(self.comConfig["path"])

            DATETIME = time.strftime('%Y%m%d-%H%M%S')
            hist = [self.userId, "BACKUP", "Backup", DATETIME, self.userData["user_name"]]
            self.dblog.writeHistory(hist)

            db = self.configDB["database"]
            host = self.configDB["host"]
            user = self.configDB["user"]
            pwd = self.configDB["password"]
            oripwd = encdec.decrypt(pwd.encode())
            
            dumpcmd = "mysqldump -h " + host + " -u " + user + " -p" + oripwd + " " + db + \
                " > " + pipes.quote(self.comConfig["path"]) + "/" + db + "_" + DATETIME + ".bak"
            os.system(dumpcmd)
            gzipcmd = "gzip " + \
                pipes.quote(self.comConfig["path"]) + "/" + db + "_" + DATETIME + ".bak"
            os.system(gzipcmd)
            self.showMessage("Backup Done!")
