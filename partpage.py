""" partpage.py - Copyright Ricky sutanto """


from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QDesktopWidget, QDialog, QMessageBox, QLineEdit, QTextEdit, QLabel, QAbstractItemView, QTableWidgetItem)

import resource
import dbconn
import logging
import mainpage
import dblogging

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("partpage")


class partWindow(QDialog):
    def __init__(self, userdata):
        super(partWindow, self).__init__()
        self.userData = userdata
        self.userId = userdata.get("user_id")
        self.updateMode = 0
    
    def _show(self, conn):
        loadUi("partscreen.ui", self)
        self.conn = conn
        self.dblog = dblogging.dbLogging(self.conn)
        self.tblPart.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tblPart.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblPart.itemSelectionChanged.connect(self.show_row)
        self.tblPart.cellClicked.connect(self.show_row)
        self.butSearch.clicked.connect(self.searchData)
        self.butClose.clicked.connect(self.closewin)
        self.butNew.clicked.connect(self.newData)
        self.butDelete.clicked.connect(self.deleteData)
        self.butUpdate.clicked.connect(self.updateData)
        self.eSearch.keyPressEvent = self.on_searchPressed
        
        self.tblPart.setColumnWidth(0, 120)
        self.tblPart.setColumnWidth(1, 300)
        self.tblPart.setColumnWidth(2, 150)
        self.tblPart.setColumnWidth(3, 0)
        self.tblPart.setColumnWidth(4, 0)
        self.tblPart.setRowHeight(0, 110)
        self.tblPart.setRowHeight(1, 110)
        res = self.showList()
        if res != None:
            self.tblPart.selectRow(0)
            self.tblPart.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            event.accept()

    def showList(self):
        while (self.tblPart.rowCount() > 0):
            self.tblPart.removeRow(0)
        result = self.dblog.getPartNumberList()
        if result != None:
            for row in result:
                stPartNo = row.get("tpl_partno").decode("utf-8")
                stFile = row.get("tpl_file").decode("utf-8")
                #print('stFile', stFile)
                iFieldCnt = int(row.get("tpl_fieldcnt"))
                iTplId = str(row.get("tpl_id"))
                iMap   = str(row.get("sn_mapping"))
                pattern = ""
                for i in range(iFieldCnt):
                    pattern += row.get("tpl_field"+str(i+1)).decode("utf-8") + "\n"
                rowCount = self.tblPart.rowCount()
                self.tblPart.setRowCount(rowCount+1)
                self.tblPart.setRowHeight(rowCount, 120)
                self.tblPart.setItem(rowCount, 0, QTableWidgetItem(stPartNo))
                self.tblPart.setItem(rowCount, 1, QTableWidgetItem(pattern))
                self.tblPart.setItem(rowCount, 2, QTableWidgetItem(stFile))
                self.tblPart.setItem(rowCount, 3, QTableWidgetItem(iTplId))
                self.tblPart.setItem(rowCount, 4, QTableWidgetItem(iMap))
        return result

    def on_searchPressed(self, event):
        if event.key() == Qt.Key_Return:
            self.searchData()
        else:
            QLineEdit.keyPressEvent(self.eSearch, event)
    

    def closewin(self):
        self.close()
    
    def searchData(self):
        self.eDeviceFile.setText("")
        
        name = self.eSearch.text().lower()
        for row in range(self.tblPart.rowCount()):
            partNo = self.tblPart.item(row, 0).text().lower()
            pattern = self.tblPart.item(row, 1).text().lower()
            #print(loginid, loginname)
            if name == "":
                hide = False
            else:
                hide = True
                try:
                    if partNo.index(name) > -1:
                        hide = False
                except ValueError:
                    pass

                try:
                    if pattern.index(name) > -1:
                        hide = False
                except ValueError:
                    pass
            #print(hide)
            # if the search is *not* in the item's text *do not hide* the row
            self.tblPart.setRowHidden(row, hide)
    
    

    def show_row(self):
        item = self.tblPart.selectedItems()
        #print(item)
        if item == None:
            return
        if item == []:
            return
        self.ePartNo.setText(item[0].text())
        self.eTemplate.setText(item[1].text())
        self.eDeviceFile.setText(item[2].text())
        i = int(item[4].text())
        self.cbMapping.setCurrentIndex(i)

    def newData(self):
        if self.updateMode == 1: return
        self.updateMode = 1  # insert mode
        self.ePartNo.setText("")
        self.eTemplate.setText("")
        self.eDeviceFile.setText("")
        self.cbMapping.setCurrentIndex(0)

        rowCount = self.tblPart.rowCount()
        self.tblPart.setRowCount(rowCount+1)
        self.tblPart.setItem(
            rowCount, 0, QTableWidgetItem(""))
        self.tblPart.setItem(
            rowCount, 1, QTableWidgetItem(""))
        self.tblPart.setItem(
            rowCount, 2, QTableWidgetItem(""))
        self.tblPart.setItem(
            rowCount, 3, QTableWidgetItem(""))
        self.tblPart.setItem(
            rowCount, 4, QTableWidgetItem("0"))
        self.tblPart.selectRow(rowCount)
        self.ePartNo.setFocus()

    def deleteData(self):
        item = self.tblPart.selectedItems()
        tplId = ""
            
        stPartNo = item[0].text()
        if self.updateMode == 0:  # update
            tplId = int(item[3].text())
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("Delete partno %s ?" % (stPartNo,))
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            if msgBox.exec_() == QMessageBox.Yes:
                self.dblog.deletePartNo(tplId)
                hist = [self.userId, "PART DB", "Delete Part No", stPartNo, self.userData["user_name"]]
                self.dblog.writeHistory(hist)
                self.tblPart.removeRow(self.tblPart.currentRow())
                rowCount = self.tblPart.rowCount()
                if rowCount >= 1:
                    self.tblPart.selectRow(0)
        elif self.updateMode == 1:  # new user
            self.tblPart.selectRow(0)
            cnt = self.tblPart.rowCount()
            self.tblPart.removeRow(cnt-1)
            self.updateMode = 0

    def updateData(self):
        item = self.tblPart.selectedItems()
        #print(item)
        if self.updateMode == 1:
            partNo = self.ePartNo.text()
            deviceFile = self.eDeviceFile.text()
            template = self.eTemplate.toPlainText()
            mapping = str(self.cbMapping.currentIndex())
            if (partNo == "") or (deviceFile == "") or (template == ""):
                self.showMessage("Entry not complete!")
                return
            line = filter(None, template.split("\n"))
            line_all = list(line)

            part = [partNo, deviceFile, mapping]
            res = self.dblog.insertPartNo(part, line_all)
            if res == True:
                hist = [self.userId, "PART DB", "Add Part no", partNo, self.userData["user_name"]]
                self.dblog.writeHistory(hist)
                self.showMessage("Part No Added!")
                res = self.showList()
                if res != None:
                    rowCount = self.tblPart.rowCount()
                    if rowCount >= 1:
                        self.tblPart.selectRow(rowCount-1)
                    self.tblPart.setFocus()
            self.updateMode = 0
        elif self.updateMode == 0:
            if item == None: return
            if item == []: return
            tplId  = item[3].text()
            partNo = self.ePartNo.text()
            deviceFile = self.eDeviceFile.text()
            template = self.eTemplate.toPlainText()
            mapping = str(self.cbMapping.currentIndex())
            if (partNo == "") or (deviceFile == "") or (template == ""):
                self.showMessage("Entry not complete!")
                return

            line = filter(None, template.split("\n"))
            line_all = list(line)
            part = [partNo, deviceFile, mapping, tplId]
            res = self.dblog.updatePartNo(part, line_all)
            if res == True:
                xi = self.tblPart.currentRow()
                hist = [self.userId, "PART DB", "Update Part No", partNo, self.userData["user_name"]]
                self.dblog.writeHistory(hist)
                self.showMessage("Part no. Updated!")
                res = self.showList()
                if res != None:
                    self.tblPart.selectRow(xi)
                    self.tblPart.setFocus()

    def showMessage(self, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()
        

