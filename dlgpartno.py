""" dlgpartno.py - Copyright Ricky sutanto """

from PyQt5.uic import loadUi
from PyQt5.QtCore import (Qt, QSize)
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QDialog, QComboBox, QSizePolicy, QMessageBox, QLineEdit)

import resource
import dblogging
import logging
import markpage

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("dlgpartno")


class WinPartNo(QDialog):
    def __init__(self, conn, userdata):
        super(WinPartNo, self).__init__()
        self.jobdata = None
        self.dblog = conn
        self.userdata = userdata
        self.userId = userdata.get("user_id")
        self.partData = None
        self.dataBatch = None

    def _show(self):
        loadUi("PartCombo.ui", self)
        self.cbPartNumber.setEditable(False)
        # self.cbPartNumber.setMinimumHeight(50)
        self.cbPartNumber.setIconSize(QSize(48, 48))
        self.cbPartNumber.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.cbPartNumber.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        result = self.dblog.getPartNumber()
        if result != None:
            # print(result)
            datalist = []
            for row in result:
                datalist.append(row["tpl_partno"].decode("utf-8"))
            self.cbPartNumber.addItems(datalist)
        self.eBatch.setText("")
        self.eSN.setText("")
        self.eQty.setValue(0)
        self.cbRemark.setChecked(False)
        level = self.userdata.get("user_role")
        if level == 1:
            self.cbRemark.hide()
        self.butConfirm.clicked.connect(self.confirm)
        self.butCancel.clicked.connect(self.closewin)
        # self.eBatch.textChanged.connect(self.CheckJob)
        self.cbRemark.stateChanged.connect(self.remarkCheck)
        self.eBatch.keyPressEvent = self.batchPress
        self.eBatch.focusOutEvent = self.batchOut
        self.cbPartNumber.currentIndexChanged.connect(self.partChange)

        globals()["tplLine1"] = ""
        globals()["tplLine2"] = ""
        globals()["tplLine3"] = ""
        globals()["tplLine4"] = ""
        globals()["tplLine5"] = ""
        globals()["tplLine6"] = ""

        markpage.markWindow.PartNoData = ""
        markpage.markWindow.BatchNo = ""
        markpage.markWindow.SerialNo = ""
        markpage.markWindow.QtyMark = 0
        markpage.markWindow.isRemark = False
        markpage.markWindow.SeqNo = 1
        markpage.markWindow.LastSN = ""
        markpage.markWindow.FirstSN = ""

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            event.accept()

    def partChange(self, index):
        self.eBatch.setText("")
        self.eSN.setText("")
        self.eQty.setValue(0)
        self.eBatch.setFocus()

    def batchPress(self, event):
        if event.key() == Qt.Key_Return:
            self.eSN.setFocus()
            '''
            pn = self.cbPartNumber.currentText()
            result = self.dblog._getPartNumberData(pn)
            self.partData = result
            if result != None:
                fieldCnt = self.partData.get("tpl_fieldcnt")
                for x in range(fieldCnt):
                    fName = "tpl_field" + str(x+1)
                    sName = "tplLine" + str(x+1)
                    txt = self.partData.get(fName)
                    globals()[sName] = txt.decode("utf-8")
            
            self.eSN.setText("")
            self.eQty.setValue(0)
            self.cbRemark.setChecked(False)
            #print("BatchPress")
            self.CheckJob()'''
        else:
            QLineEdit.keyPressEvent(self.eBatch, event)

    def batchOut(self, focusevent):
        if focusevent.lostFocus() and self.eBatch.text() != "":
            pn = self.cbPartNumber.currentText()
            result = self.dblog._getPartNumberData(pn)
            self.partData = result
            if result != None:
                fieldCnt = self.partData.get("tpl_fieldcnt")
                for x in range(fieldCnt):
                    fName = "tpl_field" + str(x+1)
                    sName = "tplLine" + str(x+1)
                    txt = self.partData.get(fName)
                    globals()[sName] = txt.decode("utf-8")

            self.eSN.setText("")
            self.CheckJob()
            # self.eQty.setValue(0)
            # if not self.cbRemark.isChecked():
            #print("check job")
            # self.cbRemark.setChecked(False)

        else:
            QLineEdit.focusOutEvent(self.eBatch, focusevent)

    def closewin(self):
        self.close()

    def confirm(self):
        pn = self.cbPartNumber.currentText()
        bn = self.eBatch.text()
        sn = self.eSN.text()
        if bn == "":
            self.showMessage("Batch No must not empty!")
            return

        if self.cbRemark.isChecked():
            isSNExists = self.traceLine()
            if sn != "" and bn != "":
                ck = self.dblog.isSNOK(bn, pn, sn)
                if ck:
                    self.showMessage("Invalid Serial No")
                    return
            else:
                if isSNExists and sn == "":
                    self.showMessage("Please complete data.")
        else:
            isSNExists = self.traceLine()
            if self.dataBatch == None:
                maxSn = 0
            else:
                maxSn = self.dataBatch.get("prd_sn")
                if maxSn == None:
                    maxSn = 0

            iQty = int(self.eQty.value())
            if iQty <= 0:
                self.showMessage("Wrong qty!")
                return

            iBal = iQty - maxSn
            if iBal <= 0:
                self.showMessage("No more S/N to mark! ")

                return
            #print("isSNExits", isSNExists)
            if iQty != 0 and bn != "":
                if isSNExists and sn == "":
                    self.showMessage("Please entry S/N.")
                    self.eQty.setFocus()
                    return

            elif sn != "" and bn != "":
                ck = self.dblog.isSNOK(bn, pn, sn)
                if ck:
                    self.showMessage("Invalid Serial No")
                    self.eQty.setFocus()
                    return

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText(
            "Are You sure all data are correct?")
        msgBox.setStandardButtons(
            QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        if msgBox.exec_() == QMessageBox.Ok:
            markpage.markWindow.PartNoData = self.cbPartNumber.currentText()
            markpage.markWindow.BatchNo = self.eBatch.text()
            markpage.markWindow.SerialNo = self.eSN.text()
            markpage.markWindow.QtyMark = self.eQty.value()
            markpage.markWindow.isRemark = self.cbRemark.isChecked()
            markpage.markWindow.SeqNo = 1
            if markpage.markWindow.isRemark == False:
                if self.dataBatch == None:
                    markpage.markWindow.FirstSN = self.eSN.text()
                    markpage.markWindow.LastSN = ""
                else:
                    txtSN = self.dataBatch.get("min_serialno")
                    if txtSN == None:
                        markpage.markWindow.FirstSN = self.eSN.text()
                    else:
                        markpage.markWindow.FirstSN = txtSN
                    txtLast = self.dataBatch.get("prd_serialno")
                    if txtLast == None:
                        markpage.markWindow.LastSN = ""
                    else:
                        markpage.markWindow.LastSN = txtLast
                pn = markpage.markWindow.PartNoData
                bn = markpage.markWindow.BatchNo
                sn = markpage.markWindow.SerialNo
                qt = markpage.markWindow.QtyMark
                if self.dataBatch == None:
                    job = [pn, bn, sn, str(qt), str(self.userId)]
                    self.dblog.saveJob(job)
            self.closewin()

    def CheckJob(self):
        #print("check job")
        pn = self.cbPartNumber.currentText()
        bn = self.eBatch.text()
        result = self.dblog.getJob(pn, bn)
        if result != None:

            if (result.get("job_partno") == pn) and (result.get("job_batchno") == bn):
                maxQty = result.get("job_qty")
                res2 = self.dblog.checkBatch(bn, pn)
                if res2 != None:
                    #print("res2", res2)
                    #sn = res2.get("prd_serialno")
                    isSNExists = self.traceLine()
                    if isSNExists and self.cbRemark.isChecked():
                        self.eQty.setReadOnly(True)
                    maxSn = res2.get("prd_sn")
                    if maxQty == maxSn and not self.cbRemark.isChecked():
                        self.showMessage("No more S/N to mark! ")
                        self.dataBatch = res2
                        # self.eSN.setReadOnly(True)
                        # self.eQty.setReadOnly(True)
                        self.eBatch.setText("")
                        self.eBatch.setFocus()
                        return
                    sn = res2.get("prd_serialno")
                    if sn != None:
                        stSn = self._formattingSN(sn, 1)
                        self.eSN.setText(stSn)
                    else:
                        self.eSN.setText(result.get("job_serialno"))
                else:
                    self.eSN.setText(result.get("job_serialno"))

                self.dataBatch = res2
                # self.eSN.setReadOnly(True)
                # self.eSN.setEnabled(False)
                if not self.cbRemark.isChecked():
                    qt = result.get("job_qty")
                    self.eQty.setValue(qt)
                    self.eSN.setReadOnly(False)
                self.eQty.setReadOnly(True)
            else:
                self.dataBatch = None
                self.eSN.setReadOnly(False)
                self.eQty.setReadOnly(False)
                self.eSN.setFocus()
        else:
            self.dataBatch = None
            self.eSN.setReadOnly(False)
            self.eQty.setReadOnly(False)
            self.eSN.setFocus()
        return result

    def remarkCheck(self):
        #print("remarkCheck:", self.cbRemark.isChecked())
        if self.cbRemark.isChecked():
            self.eSN.setText("")
            self.eSN.setReadOnly(False)
            self.eQty.setValue(1)
            self.eQty.setReadOnly(True)
            # self.eSN.setFocus()
            self.eBatch.setText("")
            self.eBatch.setFocus()
        else:
            if self.eBatch.text() != "":
                # print("RemarkCheck")
                self.CheckJob()
            else:
                self.eSN.setReadOnly(False)
                self.eQty.setReadOnly(False)

    def _formattingSN(self, txt, idx):
        st = txt
        if st == "":
            st = self.eSN.text()
            idx = 0
        result = None
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

    def showMessage(self, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()

    def traceLine(self):
        out = False
        if self.partData == None:
            pn = self.cbPartNumber.currentText()
            self.partData = self.dblog._getPartNumberData(pn)

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
