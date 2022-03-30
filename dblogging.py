""" dblogging.py - Copyright Ricky sutanto """

import dbconn
import logging
import datetime


logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger("dblogging")

class dbLogging(object):
    def __init__(self,dbObject ):
        self.con = dbObject
        self.key = "S4tu1tu3s4"

    def writeHistory(self, structData):
        data = structData
        cur = self.con.get_connection().cursor()
        x = datetime.datetime.now()
        nowdate = x.strftime("%Y-%m-%d %H:%M:%S")
        with cur:
            sql = '''INSERT INTO `mk_history` (his_datetime, his_userid, his_modul, his_action, his_description, his_username) 
                    values(%s, %s, %s, %s, %s, %s)
                    '''
            cur.execute(sql, (nowdate, data[0], data[1], data[2], data[3], data[4]))
            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False

    def writeProduction(self, structData):
        data = structData
        cur = self.con.get_connection().cursor()
        x = datetime.datetime.now()
        nowdate = x.strftime("%Y-%m-%d %H:%M:%S")
        with cur:
            '''desc = ""
            sql = "SELECT prd_serialno from mk_production where tpl_partno = %s and prd_batchno = %s and prd_serialno = %s"
            cur.execute(sql, (data[1], data[2], data[3]))
            result = cur.fetchone()
            #print ("result", result)
            if result != None:
                sn = result.get("prd_serialno")
                if sn == data[3]:
                    #print("sn:", sn)
                    desc = data[5]
            '''    

            sql = '''INSERT INTO `mk_production` (prd_datetime, prd_userid, tpl_partno, prd_batchno, prd_serialno, prd_status, prd_description, prd_sn) 
                    values(%s, %s, %s, %s, %s, %s, %s, %s)
                    '''
            cur.execute(
                sql, (nowdate, data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False
            
    def _getUserLoginDate(self, uid):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select his_datetime from mk_history where his_userid = %s and his_modul = 'AUTH' and his_action = 'LOG-IN' order by his_id desc limit 1"
            cur.execute(sql, (uid))
            return cur.fetchone()

    def _getPartNumberData(self, pn):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select AES_DECRYPT(unhex(tpl_file), SHA2('"+self.key+"',256))  as tpl_file, tpl_fieldcnt,"\
                  "AES_DECRYPT(unhex(tpl_field1), SHA2('"+self.key+"',256)) as tpl_field1,"\
                  "AES_DECRYPT(unhex(tpl_field2), SHA2('"+self.key+"',256)) as tpl_field2,"\
                  "AES_DECRYPT(unhex(tpl_field3), SHA2('"+self.key+"',256)) as tpl_field3,"\
                  "AES_DECRYPT(unhex(tpl_field4), SHA2('"+self.key+"',256)) as tpl_field4,"\
                  "AES_DECRYPT(unhex(tpl_field5), SHA2('"+self.key+"',256)) as tpl_field5,"\
                  "AES_DECRYPT(unhex(tpl_field6), SHA2('"+self.key+"',256)) as tpl_field6, sn_mapping "\
                  "from mk_pattern where tpl_partno = hex(AES_ENCRYPT(%s, SHA2('"+self.key+"',256)))"
            
            cur.execute(sql, (pn))
            return cur.fetchone()

    def _getSNMapping(self, id):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select * from mk_sn_mapping where sn_id = %s"
            cur.execute(sql, (id))
            return cur.fetchone()

    def checkBatch(self, batchno, partno):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select max(prd_sn) as prd_sn, max(prd_serialno) as prd_serialno , min(prd_serialno) as min_serialno from mk_production where prd_batchno = %s and tpl_partno = %s"
            cur.execute(sql, (batchno, partno))
            return cur.fetchone()

    def isSNOK(self, batchno, partno, sn):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select prd_serialno from mk_production where prd_batchno = %s and tpl_partno = %s and prd_serialno = %s"
            cur.execute(sql, (batchno, partno, sn))
            ret = cur.fetchone()
            if ret != None:
                stSN = ret.get("prd_serialno")
                #print(stSN)
                if stSN != None:
                    return False
                else:
                    return True
            else:
                return True

    def getPartNumber(self):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select  AES_DECRYPT(unhex(tpl_partno), SHA2('"+self.key + \
                "',256))  as tpl_partno from mk_pattern order by tpl_id"
            cur.execute(sql)
            return cur.fetchall()

    def getUserlist(self, record):
        cur = self.con.get_connection().cursor()
        with cur:
            userid = record.get("user_id")
            userrole= record.get("user_role")
            if userrole < 3:
                sql = "select * from mk_users where user_id = %s"
                cur.execute(sql, (str(userid)))
            else:
                sql = "select * from mk_users"
                cur.execute(sql)
            return cur.fetchall()

    def deleteUser(self, uid):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "delete from mk_users where user_id = %s"
            cur.execute(sql, (uid))
            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False

    def insertUser(self, structData):
        data = structData
        cur = self.con.get_connection().cursor()
        
        with cur:
            sql = '''INSERT INTO `mk_users` (user_login, user_name, user_pwd, user_status, user_role) 
                    values(%s, %s, hex(AES_ENCRYPT(%s, SHA2('S4tu1tu3s4',256))), %s, %s)
                    '''
            cur.execute(sql, ( data[0], data[1], data[2], data[3], data[4]))
            self.con._commit()
            if cur.rowcount > 0: return True
            else: return False

    def updateUser(self, structData, setPass= False):
        data = structData
        cur = self.con.get_connection().cursor()

        with cur:
            if setPass == True:
                sql = '''update `mk_users` set user_login = %s, user_name = %s, user_pwd = hex(AES_ENCRYPT(%s, SHA2('S4tu1tu3s4',256))), user_status = %s, user_role = %s where user_id = %s'''
                cur.execute(sql, (data[0], data[1], data[2], data[3], data[4], data[5]))
            else:
                sql = '''update `mk_users` set user_login = %s, user_name = %s, user_status = %s, user_role = %s where user_id = %s'''
                cur.execute(sql, (data[0], data[1], data[2], data[3], data[4]))
            
            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False

    def getPartNumberList(self):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select tpl_id, AES_DECRYPT(unhex(tpl_partno), SHA2('"+self.key+"', 256)) as tpl_partno, "\
                  "AES_DECRYPT(unhex(tpl_file), SHA2('"+self.key+"', 256)) as tpl_file, tpl_fieldcnt, "\
                  "AES_DECRYPT(unhex(tpl_field1), SHA2('"+self.key+"', 256)) as tpl_field1, "\
                  "AES_DECRYPT(unhex(tpl_field2), SHA2('"+self.key+"', 256)) as tpl_field2, "\
                  "AES_DECRYPT(unhex(tpl_field3), SHA2('"+self.key+"', 256)) as tpl_field3, "\
                  "AES_DECRYPT(unhex(tpl_field4), SHA2('"+self.key+"', 256)) as tpl_field4, "\
                  "AES_DECRYPT(unhex(tpl_field5), SHA2('"+self.key+"', 256)) as tpl_field5, "\
                  "AES_DECRYPT(unhex(tpl_field6), SHA2('"+self.key+"', 256)) as tpl_field6, sn_mapping "\
                  "from mk_pattern "
            
            cur.execute(sql)
            return cur.fetchall()

    def insertPartNo(self, structData, template):
        data = structData
        cur = self.con.get_connection().cursor()
        tpl = ['NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
        x = len(template)
        for i in range(x):
            line = template[i].replace("%", "%%")
            tpl[i] = "hex(AES_ENCRYPT('"+line+"', SHA2('S4tu1tu3s4', 256)))"
    
        with cur:
            sql = "INSERT into mk_pattern (tpl_partno, tpl_file, tpl_fieldcnt, tpl_field1, tpl_field2, tpl_field3, tpl_field4, tpl_field5, tpl_field6, sn_mapping) " + \
            " values (hex(AES_ENCRYPT(%s, SHA2('S4tu1tu3s4',256))), hex(AES_ENCRYPT(%s, SHA2('S4tu1tu3s4',256))), %s ," + \
            tpl[0] + "," + tpl[1] + "," + tpl[2] + "," + tpl[3] + "," + tpl[4] + "," + tpl[5] + ", %s)"
            print("sql", sql)
            cur.execute(sql, (data[0], data[1], x, data[2]))
            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False

    def updatePartNo(self, structData, template):
        data = structData
        cur = self.con.get_connection().cursor()
        
        tpl = ['NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
        x = len(template)
        for i in range (x):
            line = template[i].replace("%", "%%")
            tpl[i] = "hex(AES_ENCRYPT('"+line+"', SHA2('S4tu1tu3s4', 256)))"
            

        with cur:
            sql = "update mk_pattern set tpl_partno = hex(AES_ENCRYPT(%s, SHA2('S4tu1tu3s4',256))), tpl_file = hex(AES_ENCRYPT(%s, SHA2('S4tu1tu3s4',256))), " + \
                 "tpl_field1 = " + tpl[0] + ", tpl_field2 = " + tpl[1] + ", tpl_field3 = " + tpl[2] + ", tpl_field4 = " + tpl[3] + ", tpl_field5 = " + tpl[4] + \
                 ", tpl_field6 = " + tpl[5] + ", tpl_fieldcnt = %s, sn_mapping = %s where tpl_id = %s"
            #print("sql", sql)
            #print(data[0])
            cur.execute(sql, (data[0],  data[1], x, data[2], data[3]))

            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False

    def deletePartNo(self, tplid):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "delete from mk_pattern where tpl_id = %s"
            cur.execute(sql, (tplid))
            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False

    def getJob(self, partNo, batchNo):
        cur = self.con.get_connection().cursor()
        with cur:
            sql = "select * from mk_jobs where job_partno = %s and job_batchno = %s"

            cur.execute(sql, (partNo, batchNo))
            return cur.fetchone()
    
    def saveJob(self, structData):
        data = structData
        cur = self.con.get_connection().cursor()

        with cur:
            sql = '''INSERT INTO `mk_jobs` (job_datetime, job_partno, job_batchno, job_serialno, job_qty, create_by_userid) 
                    values(now(), %s, %s, %s, %s, %s)
                    '''
            cur.execute(sql, (data[0], data[1], data[2],
                        data[3], data[4]))
            self.con._commit()
            if cur.rowcount > 0:
                return True
            else:
                return False

    def getReport(self, modul, dtstart, dtstop, username):
        cur = self.con.get_connection().cursor()
        stStart = dtstart
        stStop = dtstop
        #print(modul)
        stModul = ""
        if modul != "ALL":
            stModul = " and his_modul = '" + modul + "' "
    
        stUser = ""
        if username != "":
            stUser = " and his_username = '" + username + "' "
        
        
        with cur:
            sql = "select * from mk_history where his_datetime between '" + stStart + " 00:00:00' and '" + stStop + " 23:59:59' " + stModul + stUser + " order by his_datetime"
            #print(sql)
            cur.execute(sql)
            return cur.fetchall()

    def getProduction(self, dtstart, dtstop, txt):
        cur = self.con.get_connection().cursor()
        stStart = dtstart
        stStop = dtstop
        stTxt = ""
        if txt != "":
           stTxt = " and (p.prd_batchno = '" + txt + "') or  (p.prd_serialno = '" + txt + "')"

        with cur:
            sql = "select p.*, (select user_name from mk_users where user_id = p.prd_userid) as user_name from mk_production p where p.prd_datetime between '" + \
                stStart + " 00:00:00' and '" + stStop + " 23:59:59' " + \
                stTxt + " order by p.prd_datetime, p.prd_sn"
            #print(sql)
            cur.execute(sql)
            return cur.fetchall()
