""" markpage.py - Copyright Ricky sutanto 
[20 nov 21]: Tombol mark di disable sebelum proses selesai di prosedur doMarking

"""


from typing import Text
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QDesktopWidget, QDialog, QMessageBox, QInputDialog, QTextEdit, QLabel, QAbstractItemView, QTableWidgetItem)


import resource
import dbconn
import logging
import mainpage
import datetime
import dblogging
import serial
import json
import time
import comm
import dlgpartno


logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("markpage")


class markWindow(QDialog):
    PartNoData = ""
    BatchNo = ""
    SerialNo = ""
    QtyMark = 0
    isRemark = False
    LastSN = ""
    FirstSN = ""
    SeqNo = 1

    def __init__(self, userdata):
        super(markWindow, self).__init__()
        self.userData = userdata
        self.portOpen = False
        self.rs232 = None
        self.rePrint = False
        self.door = None
        self.isUseDoor = False

        global tplLine1, tplLine2, tplLine3, tplLine4, tplLine5, tplLine6
        with open("config.json") as json_data_file:
            data = json.load(json_data_file)
        self.comConfig = data["COM"]
        self.doorConfig = data["DOOR"]
        globals()["packetno"] = 0

    def _setdbconn(self, conn):
        self.conn = conn
        self.username = self.userData.get("user_name")
        #print("username: ", self.username)
        self.userId = self.userData.get("user_id")
        self.userRole = self.userData.get("user_role")
        self.dblog = dblogging.dbLogging(self.conn)
        self.lUsername.setText(self.username)
        self.logindt = datetime.datetime.now()
        result = self.dblog._getUserLoginDate(self.userId)
        if (result != None):
            self.logindt = result.get("his_datetime")
        self.clearScreen()

    def _show(self, stackedWidget):
        loadUi("markinBox.ui", self)
        self.widget = stackedWidget
        self.showMaximized()

        self.tableMark.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableMark.setColumnWidth(0, 90)
        self.tableMark.setColumnWidth(1, 100)
        self.tableMark.setColumnWidth(2, 200)

        #desktopSize = QDesktopWidget().screenGeometry()
        #self.setFixedSize(desktopSize.width(), desktopSize.height())
        self.butBack.clicked.connect(self.closewin)
        self.butJob.clicked.connect(self.inputpartnumber)
        self.butMark.clicked.connect(self.doMarking)

    def _openComPort(self):
        try:
            #print("Open Port")
            self.rs232 = None
            self.rs232 = comm.Comm(self.comConfig)
            self.lComPort.setText("COM Connected.")
            self.rs232.comclose()
            self.rs232.comopen()

            self.portOpen = True

        except:
            self.lComPort.setText("COM Error.")
            self.portOpen = False

    def _openDoorPort(self):
        try:
            isEnabled = self.doorConfig["enabled"]
            if (isEnabled == "yes"):
                self.isUseDoor = True
                self.door = None
                self.door = comm.Comm(self.doorConfig)
                txt = self.lComPort.text()
                txt += " - Door OK"
                self.lComPort.setText(txt)
                self.door.comclose()
                self.door.comopen()

                self.portOpen = True

            else:
                self.isUseDoor = False

        except:
            txt = self.lComPort.text()
            txt += " - Door NOK"
            self.lComPort.setText(txt)
            self.portOpen = False

    def inputpartnumber(self):

        Dlg = dlgpartno.WinPartNo(self.dblog, self.userData)
        Dlg._show()
        size = Dlg.size()
        desktopSize = QDesktopWidget().screenGeometry()
        top = (desktopSize.height()/2)-(size.height()/2)
        left = (desktopSize.width()/2)-(size.width()/2)
        Dlg.move(left, top)

        Dlg.exec()

        if self.PartNoData != "":
            self.clearScreen()
            self.lPartNumber.setText(self.PartNoData)
            self.lBatch.setText(self.BatchNo)
            self.lSN.setText(self.SerialNo)
            self.lQty.setText(str(self.QtyMark))
            self.lBalance.setText(str(self.QtyMark))
            self.lLastSN.setText(self.LastSN)
            self.lFirstSN.setText(self.FirstSN)

            result = self.dblog._getPartNumberData(self.PartNoData)
            self.partData = result

            self.updateScreen()
            self.replaceBathToLine(self.lBatch.text())
            self.replaceSNToLine(self.lSN.text())
            if self.isRemark:
                iBal = 1
                self.lBalance.setText("1")
            else:
                result = self.dblog.checkBatch(self.BatchNo, self.PartNoData)
                if result != None:
                    maxSn = result.get("prd_sn")
                    if maxSn == None:
                        maxSn = 0
                    iQty = int(self.lQty.text())
                    iBal = iQty - maxSn
                    self.lBalance.setText(str(iBal))

            if iBal > 0:
                self.butMark.setEnabled(True)
            else:
                self.butMark.setEnabled(False)

    def asktoclear(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Clear & Stop Marking ?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if msgBox.exec_() == QMessageBox.Yes:
            self.clearScreen()
            hist = [self.userId, "MARKING", "CLEAR SCREEN", "", self.username]
            self.dblog.writeHistory(hist)

    def closewin(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Exit Marking ?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if msgBox.exec_() == QMessageBox.Yes:
            '''Clear Screen'''
            self.clearScreen()
            '''Log'''
            hist = [self.userId, "MARKING", "EXIT", "", self.username]
            self.dblog.writeHistory(hist)
            '''Closing RS232'''
            #print("close port")
            if self.rs232 != None:
                self.rs232.comclose()
            if self.door != None:
                self.door.comclose()

            '''Open MainWindow'''
            page = mainpage.mainWindow(self.userData)
            page._setdbconn(self.conn)
            page._show(self.widget)
            self.widget.setGeometry(0, 0, page.width(), page.height())
            self.widget.setFixedSize(page.width(), page.height())
            self.widget.setWindowTitle("MAINPAGE")
            size = page.size()
            desktopSize = QDesktopWidget().screenGeometry()
            top = (desktopSize.height()/2)-(size.height()/2)
            left = (desktopSize.width()/2)-(size.width()/2)

            self.widget.setCurrentIndex(self.widget.currentIndex()-1)
            self.widget.move(int(left), int(top))
            self.widget.setWindowTitle("MAINPAGE")
            self.close()

    def clearScreen(self):
        x = datetime.datetime.now()
        self.lProdDate.setText(x.strftime("%d/%m/%Y"))
        self.lFixed1.setText("")
        self.lFixed2.setText("")
        self.lFixed3.setText("")
        self.lFixed4.setText("")
        self.lFixed5.setText("")
        self.lFixed6.setText("")
        self.lPartNumber.setText("")
        self.lBatch.setText("")
        self.lSN.setText("")
        self.lQty.setText("")
        self.lBalance.setText("0")
        self.lFirstSN.setText("")
        self.lLastSN.setText("")
        self.lTime.setText("")
        # self.lComPort.setText("")
        self.lStatus.setText("")
        while (self.tableMark.rowCount() > 0):
            self.tableMark.removeRow(0)
        self.lUsername.setText(self.username)
        self.lTime.setText(self.logindt.strftime("%d/%m/%Y %H:%M:%S"))
        self.butMark.setEnabled(False)
        self.butJob.setEnabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()

    def updateScreen(self):
        if (self.partData != None):
            self.lFixed1.setText("")
            self.lFixed2.setText("")
            self.lFixed3.setText("")
            self.lFixed4.setText("")
            self.lFixed5.setText("")
            self.lFixed6.setText("")
            globals()["tplLine1"] = ""
            globals()["tplLine2"] = ""
            globals()["tplLine3"] = ""
            globals()["tplLine4"] = ""
            globals()["tplLine5"] = ""
            globals()["tplLine6"] = ""
            self.butMark.setEnabled(False)

            fieldCnt = self.partData.get("tpl_fieldcnt")
            for x in range(fieldCnt):
                fName = "tpl_field" + str(x+1)
                lName = "lFixed" + str(x+1)
                sName = "tplLine" + str(x+1)
                txt = self.partData.get(fName)
                #print("txt", txt)
                label = self.findChild(QLabel, lName)
                label.setText(txt.decode("utf-8"))
                globals()[sName] = txt.decode("utf-8")

                try:
                    idx = label.text().index("%m%Y")
                    if idx != -1:
                        x = datetime.datetime.now()
                        dt = x.strftime("%m%Y")
                        txt = label.text().replace("%m%Y", dt)
                        label.setText(txt)
                        globals()[sName] = txt

                except ValueError:
                    continue

    def doChange(self):
        if self.butMark.isEnabled():
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("Change Batch# ?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            if msgBox.exec_() == QMessageBox.Yes:
                hist = [self.userId, "MARKING",
                        "CHANGE BATCH#", "Commit", self.username]
                self.dblog.writeHistory(hist)
                self.lFixed1.setText(globals()["tplLine1"])
                self.lFixed2.setText(globals()["tplLine2"])
                self.lFixed3.setText(globals()["tplLine3"])
                self.lFixed4.setText(globals()["tplLine4"])
                self.lFixed5.setText(globals()["tplLine5"])
                self.lFixed6.setText(globals()["tplLine6"])
                self.lBalance.setText("0")
                self.lFirstSN.setText("")
                self.lLastSN.setText("")
                self.lBatch.setText("")
                self.lSN.setText("")
                self.lQty.setText("")
                while (self.tableMark.rowCount() > 0):
                    self.tableMark.removeRow(0)
                self.butMark.setEnabled(False)
                globals()["packetno"] = 0
            else:
                hist = [self.userId, "MARKING",
                        "CHANGE BATCH#", "Cancel", self.username]
                self.dblog.writeHistory(hist)

    def on_batchPressed(self, event):
        if event.key() == Qt.Key_Return:
            if self.lBatch.text() != "":
                bn = self.lBatch.text()
                part = self.lPartNumber.text()
                self.dbSNData = self.dblog.checkBatch(bn, part)
                # print(self.dbSNData)
                if (self.dbSNData != None) and (self.dbSNData.get("prd_sn") != None):
                    pMax = self.dbSNData.get("prd_sn")
                    pSN = self.dbSNData.get("prd_serialno")
                    sn = self._formattingSN(pSN, 1)
                    self.lSN.setText(sn)
                    self.on_snPressed(event)
                    # self.replaceSNToLine(sn)
                    self.lFirstSN.setText(sn)
                else:
                    self.lSN.setText("")

                self.lQty.setText("")

                self.replaceBathToLine(bn)
                if (self.dbSNData == None) or (self.dbSNData.get("prd_sn") == None):
                    self.lSN.setFocus()
                else:
                    self.lQty.setFocus()
                self.lBalance.setText("0")
                globals()["packetno"] = 0
        else:
            QTextEdit.keyPressEvent(self.lBatch, event)

    def on_snPressed(self, event):
        if event.key() == Qt.Key_Return:
            sn = self.lSN.text()

            self.replaceSNToLine(sn)
            self.lFirstSN.setText(sn)
            self.lQty.setFocus()
        else:
            QTextEdit.keyPressEvent(self.lSN, event)

    def validateSN(self, qty):
        go = False
        self.butMark.setEnabled(False)
        self.SerNotOk = False
        bt = self.lBatch.text()
        if bt == "":
            self.showMessage("Please input Batch No First!")
            return False
        if self.lSN.text() != "":
            part = self.lPartNumber.text()
            sn = self.lSN.text()
            isOk = self.dblog.isSNOK(bt, part, sn)
            # print("isok:",isOk)
            if isOk == False:
                self.SerNotOk = True
                if self.userRole < 2:
                    self.showMessage(
                        "Serial Already Print, need spv or admin to reprint it!")
                    self.rePrint = False
                    self.butMark.setEnabled(False)
                    go = False

                else:
                    go = True
            else:
                go = True
            if go == True:
                qtyMark = qty
                isSNExists = self.traceLine()
                if isSNExists and self.lSN.text() == "":
                    #print("Error 5")
                    self.showMessage("Please entry S/N.")
                    return False
                found = False
                if isSNExists and self.lSN.text() != "":
                    sn = self.lSN.text()
                    pn = self.lPartNumber.text()
                    bn = self.lBatch.text()

                    for x in range(qtyMark):
                        if x > 0:
                            snfrmt = self._formattingSN(sn, 1)
                            # print(snfrmt)
                            cek = self.dblog.isSNOK(bn, pn, snfrmt)
                            if cek == False:
                                self.butMark.setEnabled(False)
                                if self.userRole < 2:
                                    self.showMessage("Invalid Quantity")
                                    self.lQty.selectAll()
                                found = True
                                break
                            else:
                                sn = snfrmt

                if (found == False) and (self.SerNotOk == False):
                    self.rePrint = False
                    self.butMark.setEnabled(True)
                    return True
                else:
                    if self.userRole >= 2:
                        msgBox = QMessageBox()
                        msgBox.setIcon(QMessageBox.Question)
                        msgBox.setText(
                            "At least one S/N already print, do you want reprint it again ?")
                        msgBox.setStandardButtons(
                            QMessageBox.Yes | QMessageBox.No)
                        msgBox.setDefaultButton(QMessageBox.No)
                        if msgBox.exec_() == QMessageBox.Yes:
                            hist = [self.userId, "MARKING",
                                    "Reprint", sn, self.username]
                            self.dblog.writeHistory(hist)
                            self.butMark.setEnabled(True)
                            self.rePrint = True
                            return True
                        else:
                            self.butMark.setEnabled(False)
                            self.rePrint = False
                            return False
                    else:
                        self.butMark.setEnabled(False)
                        self.rePrint = False
                        return False
            else:
                self.rePrint = False
                return False

    def on_qtyPressed(self, event):
        if event.key() == Qt.Key_Return:
            qtyMark = int(self.lQty.text())

            self.butMark.setEnabled(True)
        else:
            if event.key() in (Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_Delete, Qt.Key_Backspace):
                QTextEdit.keyPressEvent(self.lQty, event)
            else:
                return

    def replaceBathToLine(self, bn):
        fieldCnt = self.partData.get("tpl_fieldcnt")
        for x in range(fieldCnt):
            fName = "lFixed" + str(x+1)
            label = self.findChild(QLabel, fName)
            try:
                idx = label.text().index("%bn")
                if idx != -1:
                    txt = label.text().replace("%bn", bn)
                    label.setText(txt)
                    break
            except ValueError:
                continue

    def replaceSNToLine(self, sn):
        fieldCnt = self.partData.get("tpl_fieldcnt")
        for x in range(fieldCnt):
            fName = "lFixed" + str(x+1)
            gName = "tplLine" + str(x+1)
            textLine = globals()[gName]
            label = self.findChild(QLabel, fName)
            try:
                idx = textLine.index("%sn")
                if idx != -1:
                    label.setText(textLine)
                    txt = label.text().replace("%sn", sn)
                    label.setText(txt)
                    break
            except ValueError:
                continue

    def showMessage(self, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()

    def traceLine(self):
        out = False
        fieldCnt = self.partData.get("tpl_fieldcnt")
        for x in range(fieldCnt):
            gName = "tplLine" + str(x+1)
            st = globals()[gName]
            try:
                idx = st.index("%sn")
                if idx != -1:
                    out = True
                    break

            except ValueError:
                continue
        return out

    def doMarking(self):
        self.butMark.setEnabled(False)
        if self.portOpen == True:
            snCnt = 0
            snBalance = 0
            thisSN = self.lSN.text()

            snCnt = self.SeqNo
            snBalance = int(self.lBalance.text())

            if snBalance > 0:
                # self.butMark.setEnabled(True)
                # self.butJob.setEnabled(False)

                pktno = globals()["packetno"] + snCnt
                #print("check door", self.isUseDoor)
                go = False

                # print(doorst)
                if self.isUseDoor:
                    doorst = self.door.checkDoor()
                    if (doorst == "C"):
                        go = True
                    elif (doorst == "O"):
                        self.showMessage("Door Open!")
                elif not self.isUseDoor:
                    go = True

                # print(go)
                if go:
                    if pktno >= 99:
                        pktno = 0
                    stStatus = self.rs232.getStatus(pktno)
                    # print(stStatus)
                    if stStatus == "Standby":
                        #lastSN =self._extractData(snBalance)
                        # self.lLastSN.setText(lastSN)
                        fieldCnt = self.partData.get("tpl_fieldcnt")
                        fileno = self.partData.get("tpl_file").decode("utf-8")
                        #print("fileno:", fileno)
                        for x in range(fieldCnt):
                            fName = "lFixed" + str(x+1)
                            #pktno += 1
                            label = self.findChild(QLabel, fName)
                            if self.rs232.sendLine(label.text(), pktno, fileno, x+1) == "ACK":
                                #print("Line %d Sent!" % x)
                                self.lStatus.setText("Processing..")
                        #pktno += 1

                        self.rs232.commitMark(pktno, fileno)

                        self.lStatus.setText("")
                        self.setTableView()
                        self.saveProduction()

                        snBalance -= 1
                        snCnt += 1
                        self.lBalance.setText(str(snBalance))
                        self.SeqNo = snCnt

                        globals()["packetno"] = pktno

                        if snBalance == 0:
                            # self.butJob.setEnabled(True)
                            self.lLastSN.setText(thisSN)
                            self.showMessage("Last serial marked.")
                        else:
                            newSN = self._extractData()
                            #print("newSN", newSN)
                            if newSN != None:
                                self.lSN.setText(newSN)
                            self.lLastSN.setText(thisSN)

                    else:
                        self.showMessage("Device not ready !")
                else:
                    if doorst != "C" and doorst != "O":
                        self.showMessage("Door problem..")

            else:
                self.showMessage("Max. balance reach!")
                self.butJob.setEnabled(True)
        else:
            self.showMessage("Error connection with Device !")

        self.butMark.setEnabled(True)

    def _extractData(self):
        if self.partData != None:
            fieldCnt = self.partData.get("tpl_fieldcnt")
            # print("cnt=",fieldCnt)

            sn = self._formattingSN(self.lSN.text(), 1)
            if sn == "":
                sn = self.lSN.text()
            for x in range(fieldCnt):
                fName = "lFixed" + str(x+1)
                gName = "tplLine" + str(x+1)
                label = self.findChild(QLabel, fName)
                label.setText(globals()[gName])
                #print("ori :",label.text())

                try:
                    idx1 = label.text().index("%bn")
                    if idx1 != -1:
                        bn = self.lBatch.text()
                        txt = label.text().replace("%bn", bn)
                        label.setText(txt)
                except ValueError:
                    try:
                        idx2 = label.text().index("%sn")
                        if idx2 != -1:
                            #print("formating now")

                            #print("sn =", sn)
                            # self.eSN.setText(sn)
                            txt = label.text().replace("%sn", sn)
                            label.setText(txt)

                    except ValueError:
                        pass

                #print("next :", label.text())
        return sn

    def _formattingSN(self, txt, idx):
        st = txt
        if st == "":
            st = self.lSN.text()
            idx = 0
        result = ""
        alpha = ""
        final = ""
        try:
            snMapping = self.partData.get("sn_mapping")
            result = self.dblog._getSNMapping(str(snMapping))
            self.SnMappingData = result
            if self.SnMappingData != None:
                fixStart = self.SnMappingData.get("sn_fix_pos")
                fixLen = self.SnMappingData.get("sn_fix_len")
                alphaStart = self.SnMappingData.get("sn_alpha_pos")
                alphaLen = self.SnMappingData.get("sn_alpha_len")
                numPos = self.SnMappingData.get("sn_numeric_pos")
                numLen = self.SnMappingData.get("sn_numeric_len")
                totLen = self.SnMappingData.get("sn_total_len")
                lz = self.SnMappingData.get("sn_leadingzero")

                if fixStart != -1:
                    result = st[fixStart-1:fixLen]
                    # print("fix:",result)

                if alphaStart != -1:
                    alpha = st[alphaStart-1:alphaStart-1+alphaLen]
                    #print("alpha:", alpha)

                l = len(st)
                #print("st", st)
                #print("numpos:", numPos)
                sn = st[numPos-1:l]
                #print("seq :", sn)
                stSN = int(sn)
                # if idx > 0
                if lz == True:
                    final = str(stSN+idx).zfill(numLen)
                    if (len(final) > numLen):
                        final = "1".zfill(numLen)
                        x = ord(alpha[len(alpha)-1])
                        # print(x)
                        x = x + 1
                        if x == 91:
                            x = 65
                        tmp = alpha[:len(alpha)-1]
                        # print(tmp)
                        alpha = tmp + chr(x)
                        # print(alpha)
                else:
                    final = str(stSN+idx)

                #print("final:", final)
                result = result + alpha + final
                #print("result: ", result)
        except:
            pass
        return result

    def setTableView(self):
        rowCount = self.tableMark.rowCount()
        rowCount += 1
        self.tableMark.setRowCount(rowCount)
        stDate = self.lProdDate.text()
        stBatch = self.lBatch.text()
        stSN = self.lSN.text()

        self.tableMark.setItem(rowCount-1, 0, QTableWidgetItem(stDate))
        self.tableMark.setItem(rowCount-1, 1, QTableWidgetItem(stBatch))
        self.tableMark.setItem(rowCount-1, 2, QTableWidgetItem(stSN))
        self.tableMark.setItem(
            rowCount-1, 3, QTableWidgetItem(self.lFixed1.text()))
        self.tableMark.setItem(
            rowCount-1, 4, QTableWidgetItem(self.lFixed2.text()))
        self.tableMark.setItem(
            rowCount-1, 5, QTableWidgetItem(self.lFixed3.text()))
        self.tableMark.setItem(
            rowCount-1, 6, QTableWidgetItem(self.lFixed4.text()))
        self.tableMark.setItem(
            rowCount-1, 7, QTableWidgetItem(self.lFixed5.text()))
        self.tableMark.setItem(
            rowCount-1, 8, QTableWidgetItem(self.lFixed6.text()))
        self.tableMark.setItem(rowCount-1, 9, QTableWidgetItem(self.username))

    def saveProduction(self):
        '''\
            prd_userid, tpl_partno, prd_batchno, prd_serialno, prd_status, prd_description, prd_sn
        '''

        stBatch = self.lBatch.text()
        stSN = self.lSN.text()

        stPartNo = self.lPartNumber.text()
        stSeqSN = ""
        self.dbSNData = self.dblog.checkBatch(stBatch, stPartNo)
        if (self.dbSNData != None) and (self.dbSNData.get("prd_sn") != None):
            pMax = self.dbSNData.get("prd_sn")
            if pMax != None:
                if stSN == "":
                    stSN = str(pMax + 1)
                stSeqSN = str(pMax + 1)
            else:
                stSeqSN = "1"
        else:
            stSeqSN = "1"

        iQty = int(self.lQty.text())
        iBal = int(self.lBalance.text())
        stDesc = ""

        #print("qty vs balance", iQty, iBal)
        if iQty == iBal:
            stDesc = "Begin batch"
            #print("masuk sini")
        elif iBal == 1:
            stDesc = "End batch"
            # print("ending")

        if self.isRemark == True:
            stDesc = "Re-Mark S/N"
            stSeqSN = ""
        rect = [self.userId, stPartNo, stBatch, stSN, "1", stDesc, stSeqSN]
        self.dblog.writeProduction(rect)
