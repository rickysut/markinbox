""" production.py - Copyright Ricky sutanto """

from typing import Sequence
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QDesktopWidget, QDialog, QMessageBox, QLineEdit, QTextEdit, QLabel, QAbstractItemView, QTableWidgetItem, QFileDialog)

import resource
import dbconn
import logging
import mainpage
import dblogging
import pandas as pd
import datetime

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("production")


class Production(QDialog):
    def __init__(self, userdata):
        super(Production, self).__init__()
        self.userData = userdata
        self.userId = userdata.get("user_id")

    def _show(self, conn):
        loadUi("production.ui", self)
        self.conn = conn
        self.dblog = dblogging.dbLogging(self.conn)
        self.tblReport.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tblReport.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.butClose.clicked.connect(self.closewin)
        self.butExport.clicked.connect(self.export)
        self.butSearch.clicked.connect(self.showlist)
        self.eSearch.keyPressEvent = self.on_searchPressed
        self.tblReport.setColumnWidth(0, 150)
        self.tblReport.setColumnWidth(1, 150)
        self.tblReport.setColumnWidth(2, 150)
        self.tblReport.setColumnWidth(3, 150)
        self.tblReport.setColumnWidth(4, 150)
        self.tblReport.setColumnWidth(5, 150)
        self.tblReport.setColumnWidth(6, 150)
        self.deStart.setDate(datetime.datetime.now())
        self.deStop.setDate(datetime.datetime.now())
        self.showlist()

        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            event.accept()

    def closewin(self):
        self.close()

    def export(self):
        columnHeaders = []

        for j in range(self.tblReport.model().columnCount()):
            columnHeaders.append(self.tblReport.horizontalHeaderItem(j).text())

        filename = QFileDialog.getSaveFileName(
            self, 'Save File', '', ".xlsx(*.xlsx)")

        if filename[0] == "":
            return

        df = pd.DataFrame(columns=columnHeaders)

        for row in range(self.tblReport.rowCount()):
            if self.tblReport.isRowHidden(row):
                continue
            for col in range(self.tblReport.columnCount()):
                df.at[row, columnHeaders[col]] = self.tblReport.item(
                    row, col).text()

        df.to_excel(filename[0], index=False)
        self.showMessage("Export Done")

    def on_searchPressed(self, event):
        if event.key() == Qt.Key_Return:
            self.showlist()
        else:
            QLineEdit.keyPressEvent(self.eSearch, event)

    def showlist(self):
        txt = self.eSearch.text()
        stStart = self.deStart.date().toString("yyyy-MM-dd")
        stStop = self.deStop.date().toString("yyyy-MM-dd")
        
        while(self.tblReport.rowCount() > 0):
            self.tblReport.removeRow(0)

        result = self.dblog.getProduction(stStart, stStop, txt)
        if result != None:
            for row in result:
                dt = row.get("prd_datetime").strftime("%d-%m-%Y %H:%M:%S")
                userName = row.get("user_name")
                partno = row.get("tpl_partno")
                batchno = row.get("prd_batchno")
                ser = row.get("prd_serialno")
                desc = row.get("prd_description")
                seq  = str(row.get("prd_sn"))

                rowCount = self.tblReport.rowCount()
                self.tblReport.setRowCount(rowCount+1)
                self.tblReport.setItem(rowCount, 0, QTableWidgetItem(dt))
                self.tblReport.setItem(rowCount, 1, QTableWidgetItem(partno))
                self.tblReport.setItem(rowCount, 2, QTableWidgetItem(batchno))
                self.tblReport.setItem(rowCount, 3, QTableWidgetItem(ser))
                self.tblReport.setItem(rowCount, 4, QTableWidgetItem(seq))
                self.tblReport.setItem(rowCount, 5, QTableWidgetItem(desc))
                self.tblReport.setItem(rowCount, 6, QTableWidgetItem(userName))

    def showMessage(self, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()
