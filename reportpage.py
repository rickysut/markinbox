""" reportpage.py - Copyright Ricky sutanto """

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QDate
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QDesktopWidget, QComboBox, QDialog, QMessageBox, QLineEdit, QTextEdit, QLabel, QAbstractItemView, QTableWidgetItem, QFileDialog)

import resource
import dbconn
import logging
import mainpage
import dblogging
import datetime
import pandas as pd



logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("reportpage")


class reportWindow(QDialog):
    def __init__(self, userdata):
        super(reportWindow, self).__init__()
        self.userData = userdata
        self.updateMode = 0
        self.userId = userdata.get("user_id")

    def _show(self, conn):
        loadUi("report.ui", self)
        self.conn = conn
        self.dblog = dblogging.dbLogging(self.conn)
        self.tblReport.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tblReport.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.butClose.clicked.connect(self.closewin)
        self.butExport.clicked.connect(self.export)
        self.butFilter.clicked.connect(self.filter)
        self.butSearch.clicked.connect(self.findField)
        self.eSearch.keyPressEvent = self.on_searchPressed
        self.tblReport.setColumnWidth(0, 100)
        self.tblReport.setColumnWidth(1, 140)
        self.tblReport.setColumnWidth(2, 200)
        self.tblReport.setColumnWidth(3, 200)
        self.tblReport.setColumnWidth(4, 200)
        self.deStart.setDate(datetime.datetime.now())
        self.deStop.setDate(datetime.datetime.now())
        x = datetime.datetime.now()
        stdate1 = x.strftime("%Y-%m-%d")
        self.showList("ALL", stdate1, stdate1, "")
        

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            event.accept()

    def closewin(self):
        self.close()

    def showList(self, modul, dtstart, dtstop, username ):
        while (self.tblReport.rowCount() > 0):
            self.tblReport.removeRow(0)
        
        result = self.dblog.getReport(modul, dtstart, dtstop, username)
        if result != None:
            for row in result:
                dt = row.get("his_datetime").strftime("%Y-%m-%d")
                userName = row.get("his_username")
                module = row.get("his_modul")
                action = row.get("his_action")
                desc = str(row.get("his_description"))
                
                rowCount = self.tblReport.rowCount()
                self.tblReport.setRowCount(rowCount+1)
                self.tblReport.setItem(rowCount, 0, QTableWidgetItem(dt))
                self.tblReport.setItem(rowCount, 1, QTableWidgetItem(userName))
                self.tblReport.setItem(rowCount, 2, QTableWidgetItem(module))
                self.tblReport.setItem(rowCount, 3, QTableWidgetItem(action))
                self.tblReport.setItem(rowCount, 4, QTableWidgetItem(desc))
            
        
    def export(self):
        columnHeaders = []

        for j in range (self.tblReport.model().columnCount()):
            columnHeaders.append(self.tblReport.horizontalHeaderItem(j).text())

        filename = QFileDialog.getSaveFileName(self, 'Save File', '', ".xlsx(*.xlsx)")
        
        if filename[0] ==  "": return

        df = pd.DataFrame(columns=columnHeaders)

        for row in range(self.tblReport.rowCount()):
            if self.tblReport.isRowHidden(row): continue
            for col in range(self.tblReport.columnCount()):
                df.at[row, columnHeaders[col]] = self.tblReport.item(row, col).text()

        df.to_excel(filename[0], index=False)
        self.showMessage("Export Done")

    

    def filter(self):
        stStart = self.deStart.date().toString("yyyy-MM-dd") 
        stStop = self.deStop.date().toString("yyyy-MM-dd")
        stModule = self.cbModule.currentText()
        stUsername = self.eUsername.text()
        self.showList(stModule, stStart, stStop, stUsername)

    def on_searchPressed(self, event):
        if event.key() == Qt.Key_Return:
            self.findField()
        else:
            QLineEdit.keyPressEvent(self.eSearch, event)

    def findField(self):
        txt = self.eSearch.text().lower()
        for row in range(self.tblReport.rowCount()):
            action = self.tblReport.item(row, 3).text().lower()
            desc = self.tblReport.item(row, 4).text().lower()
            #print(action, desc)
            if txt == "":
                hide = False
            else:
                hide = True
                try:
                    if action.index(txt) > -1:
                        hide = False
                except ValueError:
                    pass

                try:
                    if desc.index(txt) > -1:
                        hide = False
                except ValueError:
                    pass
            #print(hide)
            # if the search is *not* in the item's text *do not hide* the row
            self.tblReport.setRowHidden(row, hide)

    def showMessage(self, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()
