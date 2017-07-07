#class library for MS Access related functions

import traceback
import pyodbc
from functools import reduce

import pymysql
import dateutil.parser as dparser
import datetime
import sys
from io import StringIO
import Logger

class DBAccess:
    def __init__(self, db_type = "msacccess", ms_access_path = "", host=None, port=0, db_name = "", user_id = "", pwd = ""):
        self._dbtype = db_type
        if db_type == 'msaccess':
            self._db_file = ms_access_path
            self._user = 'admin'
            self._password = ''
            if ms_access_path[-3:] == 'mdb':
                odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;UID=%s;PWD=%s' % (self._db_file,self._user, self._password)
            else: # Or, for newer versions of the Access drivers:
                odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % (self._db_file,self._user, self._password)
            try:
                self._conn = pyodbc.connect(odbc_conn_str)
            except:
                print("failed to connect the database. error details:{0}".format(traceback.print_exc()))
        elif db_type == 'mysql':
            self._host = host
            self._port = port
            self._db_name = db_name
            self._user = user_id
            self._password = pwd
            try:
                self._conn = pymysql.connect(host=host, port=port, user=user_id, passwd=pwd, db=db_name)
            except:
                print("failed to connect the database. error details:{0}".format(traceback.print_exc()))
        self._cursor = self._conn.cursor()

    def Execute(self, sql):
        return self._cursor.execute(sql)

    def InsertMany(self, strTable, lstColumns, lstValues, bAutoCommit = True):
        sql = self.prepareInsertSQL(strTable, lstColumns)

        rslt = self._cursor.executemany(sql, lstValues)
        if bAutoCommit:
            self._conn.commit()
        return rslt.rowcount

    def InsertOne(self, strTable, lstColumns, lstValues, bAutoCommit = True):
        sql = self.prepareInsertSQL(strTable, lstColumns)
        rslt = self._cursor.execute(sql, lstValues)
        if bAutoCommit:
            self._conn.commit()
        return rslt.rowcount

    def Committ(self):
        self._conn.commit()

    def prepareUpdateSQL(self, strTable, lstColumnsToUpdate, lstKeysToUpdate):
        if self._dbtype == 'msaccess':
            cols = '=?, '.join(lstColumnsToUpdate) + '=?'
            keys = '=? and '.join(lstKeysToUpdate) + '=?'
            sql = "UPDATE {0} SET {1} WHERE {2}".format(strTable, cols, keys)
        else:
            cols = '=%s, '.join(lstColumnsToUpdate) + '=%s'
            keys = '=%s and '.join(lstKeysToUpdate) + '=%s'
            sql = "UPDATE {0} SET {1} WHERE {2}".format(strTable, cols, keys)
        #print(sql)
        return sql

    def prepareInsertSQL(self, strTable, lstColumns):
        if self._dbtype == 'msaccess':
            sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(strTable, ",".join(lstColumns),",".join(['?'] * len(lstColumns)))
        else:
            sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(strTable, ",".join(lstColumns),
                                                              ",".join(['%s'] * len(lstColumns)))
        return sql

    def InsertDictionary(self, strTableName, dict, bAutoCommit = True):
        lstColumns = list(dict.keys())
        lstValues = list(dict.values())
        try:
            nRows = self.InsertOne(strTableName, lstColumns, lstValues)
            return nRows
        except:
            print(traceback.print_exc())
            return 0

    def UpdateTable(self, strTableName, lstColumnsToUpdate, lstValsToUpdate, lstKeys, lstKeyVals, bAutoCommit = True):
        sql = self.prepareUpdateSQL(strTableName, lstColumnsToUpdate, lstKeys)
        try:
            rslt = self._cursor.execute(sql, lstValsToUpdate + lstKeyVals)
            if bAutoCommit:
                self._conn.commit()
            return rslt.rowcount
        except:
            print(traceback.print_exc())
            return 0

    '''
    here keys is a list of keys used in where statement 
    '''
    def UpdateDictionary(self, strTableName, dict, keys, bAutoCommit = True):
        #first pop the elements from the keys
        dictKeyColumns = {}
        for key in keys:
            dictKeyColumns[key] = dict.pop(key)
        lstColumnsToUpdate = list(dict.keys())
        lstValuesToUpdate = list(dict.values())
        lstKeys = list(dictKeyColumns.keys())
        lstKeyValues = list(dictKeyColumns.values())
        a = '=?,'.join(lstColumnsToUpdate) + '=?'
        b =  '=? and '.join(lstKeys) + '=?'
        sql = "UPDATE {0} SET {1} WHERE {2}".format(strTableName, a, b)
        #print (sql)
        try:
            rslt = self._cursor.execute(sql, lstValuesToUpdate + lstKeyValues)
            if bAutoCommit:
                self._conn.commit()
            return rslt.rowcount
        except:
            print(traceback.print_exc())
            return 0



class db_mysql:

    def __init__(self, strHost, nPort, strUsr, strPwd, strDBName):
        self.getConnection(strHost, nPort, strUsr, strPwd, strDBName)


    def getConnection(self, _host, _port, _usr, _pwd, _DBName):
        self._conn = pymysql.connect(host=_host, port=_port, user=_usr, passwd=_pwd, db=_DBName)
        self._cur   = self._conn.cursor()

    def getColumnsList(self, strTableName):
        self._cur = self._conn.cursor()
        self._cur.execute("SELECT * FROM {0} LIMIT 1".format(strTableName))
        temp = [x[0] for x in self._cur.description]
        self._ColumnsList = ['`Range`' if x=='Range' else x for x in temp]
        #print( temp)
        return temp

    '''get the insert statement for a target table'''
    '''it retrieves all the columns of a table, and generate the sql insertion string'''
    def prepareInsertStatement(self, strTargetTable, lstColumns = None):
        #sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(strTable, ",".join(lstColumns),",".join(['?'] * len(lstColumns)))
        #return sql
        if lstColumns is None:
            lstColumns = self.getColumnsList(strTargetTable)
            lstColumns = self._ColumnsList
        else:
            self._ColumnsList = ['`Range`' if x=='Range' else x for x in lstColumns]
        #lstColumns =
        columnsList = reduce((lambda x, y: x + ', ' + y) , self._ColumnsList)
        valueList = ["%s"]* len(lstColumns)
        valueList1 = reduce((lambda x,y: x + ', ' +y), valueList)
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(strTargetTable, columnsList, valueList1)
        #print(sql)
        self._InsertSql = sql
        return sql

    '''
        prepare the update statement
    '''
    def prepareUpdateStatement(self, strTargetTable, lstColumns = None, keyColumns=None):
        if lstColumns is None:
            lstColumns = self.getColumnsList(strTargetTable)[:]
        tmpColumns = list(lstColumns)
        for item in keyColumns:
            tmpColumns.remove(item)
        lstValClause = '=%s, '.join(tmpColumns) + '=%s'
        lstWhereClause = '=%s and '.join(keyColumns) + '=%s'
        sql = "UPDATE {0} SET {1} WHERE {2}".format(strTargetTable, lstValClause, lstWhereClause)
        self._updateSql = sql
        #print(self._updateSql)

    '''params is a tuple that contains the values to insert'''
    def insertOneRecord(self, params, bAutoCommit = True):
        try:
            result = self._cur.execute(self._InsertSql, params)
        except:
            print(traceback.print_exc())
            return 0
        if bAutoCommit:
            self._conn.commit()
        return result.rowcount

    def insertManyRecord(self, dataSet, bAutoCommit=True):
        try:
            result = self._cur.executemany(self._InsertSql, dataSet)
        except:
            print(traceback.print_exc())
            return 0
        if bAutoCommit:
            self._conn.commit()
        return result.rowcount

    '''
    the data here can be a dictionary or a list/tuple of data points
    if it's a list/tuple, the column sequence must be the same as the table column sequence
    if it's a dictionary, then the keys must be the same as column names
    '''
    def updateRecord(self, strTargetTable, data, whereClauseColumns, bAutoCommit = True):
        whereData = []
        if type(data) is tuple or type(data) is list:
            for item in whereClauseColumns:
                idx = self._ColumnsList.index(item)
                if type(data) is tuple:
                    data = list(data)
                whereData.append(data.pop(idx))
            #print(data + whereData)
            try:
                self._cur.execute(self._updateSql,data + whereData)
            except:
                print(sys.exc_info())
                print(self._updateSql)
                print(data)
                nMLSNum = self.getColumnValue("MLSNum", data)
                Logger.appendToLogFile(nMLSNum, traceback.print_exc())
        else:
            #it's a dictionary
            dict = {}
            for item in whereClauseColumns:
                dict[item] = data.pop(item)

        if bAutoCommit:
            self._conn.commit()
        return 1

    def getColumnValue(self,strColumnName, dataRow):
        idx = self._ColumnsList.index(strColumnName)
        return dataRow[idx]
    '''transfers one record contained in data row to target table
    difference between transfer and insert is transfer wraps around the insert, prepares the insert sql 
    and switch to update if insert causes a primary key violation
    '''

    def transferOneRecord(self, strTargetTable, dataRow, whereClauseColumns, bAutocommit = True):
        #self.prepareInsertStatement(strTargetTable)
        self.prepareUpdateStatement(strTargetTable, self._ColumnsList, whereClauseColumns)
        if len(dataRow) != len(self._ColumnsList):
            Logger.appendToLogFile('NA', 'Error: Inconsistent data column count spotted.')
            return 0
        try:
            #first will try to insert the record
            result = self._cur.execute(self._InsertSql, dataRow)
            #print("1 new record inserted")
            if bAutocommit:
                self._conn.commit()
            #print('1 row updated to mysql')
            return 1
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062: #it's a primary key error
                #print(sys.exc_info())
                print('duplicate MLSNum found, will try to update instead')
                result = self.updateRecord(strTargetTable, dataRow, whereClauseColumns, bAutocommit)
                #print('1 record updated')
                return result
            else:
                print(sys.exc_info())
                return 0
        except pymysql.err.DatabaseError as eD:
            print(sys.exc_info())
            nMLSNum = self.getColumnValue("MLSNum", dataRow)
            Logger.appendToLogFile(nMLSNum, str(eD.args[0]) + ' ' + eD.args[1])
            return 0
        except:
            print(sys.exc_info())
            print(self._InsertSql)
            print(dataRow)
            nMLSNum = self.getColumnValue("MLSNum", dataRow)
            Logger.appendToLogFile(nMLSNum, traceback.print_exc())
            return 0
    '''
        insert the csv as sIO into AllPropertyRecords table
        the first row is the column names
    '''
    def insertHarTempoRecords(self, sIO):
        strTargetTable = 'HARTempo_AllRecords'
        #strTargetTable = 'hartempo_allrecords'
        nRowProcessed = 0
        lines = sIO.readlines()
        nRowCount = len(lines) - 1
        lines = [x.rstrip('\n') for x in lines]
        tempColumns = lines[0].split(sep='\t')
        self._ColumnsList = ['OfficeName' if x == 'o1.OfficeName' else x for x in tempColumns]
        self._InsertSql = self.prepareInsertStatement(strTargetTable, self._ColumnsList)

        for line in lines[1:]:
            dataRow = line.split(sep='\t')
            for idx, item in enumerate(dataRow):
                if len(item) == 0:
                    dataRow[idx] = None
                elif len(item) > 150:
                    dataRow[idx] = dataRow[idx][:150]
                else:
                    #test if the item is a date type, if so, convert the format
                    try:
                        dt = datetime.datetime.strptime(item, '%m/%d/%Y')
                        dataRow[idx] = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        #test if the item is a datetime type:
                        try:
                            dt = datetime.datetime.strptime(item, '%m/%d/%Y %I:%M:%S %p')
                            dataRow[idx] = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            continue

            rToInsert = tuple(dataRow)
            nRslt = self.transferOneRecord(strTargetTable, rToInsert, ["MLSNum"])
            if nRslt == 1:
                #update the last update column
                idx = self._ColumnsList.index("MLSNum")
                nMLSNum = rToInsert[idx]
                self.updateLastUpdateTime(strTargetTable, ["MLSNum"], [nMLSNum])
                nRowProcessed += nRslt
                print("Total count: {0}".format(nRowProcessed))
        return nRowProcessed

    def updateLastUpdateTime(self, strTableName, lstWhereColumns, keys, strColumnName = 'LastUpdate'):
        lstWhereClause = '=%s and '.join(lstWhereColumns) + '=%s'
        sql = "UPDATE {0} SET {1}{2} WHERE {3}".format(strTableName, strColumnName, " = %s", lstWhereClause)
        strTS = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._cur.execute(sql,[strTS] + keys)
        self._conn.commit()

    '''
    it converts elements in a list of values, to date and datetime values if they satisfies the format: M/D/YYYY HH:MM:SS 
    to a mysql date or datetime format
    '''
    def ConvertDateTimeValues(self, lstValues):
        for idx, item in enumerate(lstValues):
            try:
                dt = datetime.datetime.strptime(item, '%m/%d/%Y')
                lstValues[idx] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                # test if the item is a datetime type:
                try:
                    dt = datetime.datetime.strptime(item, '%m/%d/%Y %I:%M:%S %p')
                    lstValues[idx] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    continue

    def TransferDictionary(self, strTableName, dict, bAutoCommit = True):
        lstColumns = list(dict.keys())
        lstValues = list(dict.values())
        self.ConvertDateTimeValues(lstValues)

        try:
            nRows = self.InsertOne(strTableName, lstColumns, lstValues)
            nMLSNum = self.getColumnValue("MLSNum", lstValues)
            self.updateLastUpdateTime(strTableName, ['MLSNum'], [nMLSNum], 'OriginalTS')
            return nRows
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062: #it's a primary key error
                #print(sys.exc_info())
                print('duplicate MLSNum found, will try to update instead')
                self.UpdateDictionary(strTableName, dict, ['MLSNum'], True)
                nMLSNum = self.getColumnValue("MLSNum", lstValues)
                self.updateLastUpdateTime(strTableName, ['MLSNum'], [nMLSNum], 'LastUpdateTS')
                return 1
            else:
                print(sys.exc_info())
                return 0
        except pymysql.err.DatabaseError as eD:
            print(sys.exc_info())
            return 0
        except:
            print(sys.exc_info())
            return 0

    '''
       here keys is a list of keys used in where statement 
       '''

    def UpdateDictionary(self, strTableName, dict, keys, bAutoCommit=True):
        # first pop the elements from the keys
        dictKeyColumns = {}
        for key in keys:
            dictKeyColumns[key] = dict.pop(key)
        lstColumnsToUpdate = list(dict.keys())
        lstColumnsToUpdate = ['`Range`' if x == 'Range' else x for x in lstColumnsToUpdate]
        lstValuesToUpdate = list(dict.values())
        self.ConvertDateTimeValues(lstValuesToUpdate)
        lstKeys = list(dictKeyColumns.keys())
        lstKeyValues = list(dictKeyColumns.values())
        a = '=%s,'.join(lstColumnsToUpdate) + '=%s'
        b = '=%s and '.join(lstKeys) + '=%s'
        sql = "UPDATE {0} SET {1} WHERE {2}".format(strTableName, a, b)
        #print (sql)
        try:
            rslt = self._cur.execute(sql, lstValuesToUpdate + lstKeyValues)
            if bAutoCommit:
                self._conn.commit()
            return rslt
        except:
            print(traceback.print_exc())
            print (lstValuesToUpdate + lstKeyValues)
            return 0

    def InsertOne(self, strTable, lstColumns, lstValues, bAutoCommit = True):
        sql = self.prepareInsertStatement(strTable, lstColumns)
        rslt = self._cur.execute(sql, lstValues)
        if bAutoCommit:
            self._conn.commit()
        return rslt


'''
if __name__ == "__main__":
    #test the code
    host = '73.136.184.214'
    #host = 'localhost'
    usr = 'xiaowei'
    pwd = 'Hhxxttxs2017'
    port = 3306
    DBName = 'RealAnalysis_DEV'
    db = db_mysql(host, port, usr, pwd, DBName)
    db.prepareInsertStatement("test")
    db.prepareUpdateStatement("test", None, ['keyCol'])
    db.transferOneRecord("test",[2,'abc','2017-1-1'], ['keyCol'])
    db.transferOneRecord("test", [2, 'abc', '2017-1-1'], ['keyCol'])
    #column_list = db.getColumnsList("joblog")
    #print(column_list)
    #column_list = db.getColumnsList("ZipCodeList")
    #print(column_list)
'''
'''
if __name__ == "__main__":
    #db = MSAccess(r"c:/temp/RealAnalysis.accdb")
    db=DBAccess
    dict = {'ListAgentId': 'worker', 'CompBuyerAgent': None, 'Area': '9', 'ListBroker': 'HORE01/Homestead Realty', 'MarketArea': 'Heights/Greater Heights', 'CloseAgtTRECId': '0391794', 'YearBuilt': 1920, 'Heat': 'Central Gas', 'Baths': '2/0', 'Roof': None, 'LPperSqft': 1.29, 'PendingDate': '12/20/2015', 'LeasedPricePerSqft': 1.24, 'SchoolDistrict': '27 - Houston', 'Flooring': 'Wood', 'TaxID': '021-018-000-0030', 'SaleMLSNum': None, 'MasterBath': None, 'LotSize': 8180, 'Address': '533 Oxford Street', 'OrigPrice': None, 'LeaseAlso': None, 'AgentPhone': None, 'LotDesc': 'Other', 'HighSchool': 'HEIGHTS HIGH SCHOOL', 'UnitLevel': None, 'ListDate': '12/20/2015', 'ListAgentName': 'Kim Pedigo', 'TaxRate': None, 'Foundation': None, 'Latitude': '29.781141', 'PropertyType': 'Rental', 'BrokerAddress': 'PO Box 130385, Houston               TX 77219', 'AgentEmail': None, 'Interior': None, 'Subdivision': 'Houston Heights', 'ListPrice': 2300.0, 'CompSubAgent': None, 'WaterfrontFeat': None, 'LeaseDate': '01/01/2016', 'TotalDiscount': None, 'ApprovalRequirement': 'Yes/Good job, good credit.', 'City': 'Houston', 'Heating': 'Central Gas', 'ApplicationFee': 55.0, 'MaintFee': None, 'Countertops': 'Tiles', 'Status': 'Sold', 'TotalUnits': None, 'UnitStories': '1', 'Bonus': None, 'Longitude': '-95.392221', 'Restrictions': 'No Restrictions', 'CloseAgentId': 'WORKER', 'ListAgent': 'worker/Kim Pedigo', 'Range': 'Electric Cooktop', 'LegalDesc': 'TRS 1A 2A & 3 BLK 286 HOUSTON HEIGHTS', 'County': 'Harris', 'ListBrokerName': 'Homestead Realty', 'Stories': None, 'TDate': '12/20/2015', 'FloorLocation': None, 'Zip': '77007 - 2601', 'PropertyClass': 'Single Family Detached', 'MLSNum': '77163257', 'DateAvail': '10/23/2015', 'Access': None, 'CloseBroker': 'Homestead Realty (HORE01)', 'Style': None, 'EstCloseDate': '01/01/2016', 'CloseAgentName': 'Kim Pedigo ', 'LotValue': None, 'Acres': '/ 0 Up To 1/4 Acre', 'ListBrokerId': 'HORE01', 'Builder': None, 'MiddleSchool': 'HOGG MIDDLE SCHOOL (HOUSTON)', 'ExteriorCons': None, 'Type': None, 'LeasePrice': 2200.0, 'Cooling': 'Central Electric', 'PrivatePool': 'No', 'Location': None, 'Bedrooms': '3/', 'RentalTerm': 'One Year', 'State': 'Texas', 'BedroomsDesc': 'All Bedrooms Down', 'DaysOnMarket': '', 'CloseBrokerId': 'HORE01', 'CloseAgent': 'Kim Pedigo (WORKER)', 'SecurityDeposit': '2300', 'BldgSqft': 1780, 'MasterPlanned': None, 'LicensedSupervisor': None, 'Connections': None, 'PrvtPool': 'No', 'CloseBrokerName': 'Homestead Realty ', 'ElemSchool': 'HARVARD ELEMENTARY SCHOOL', 'Oven': 'Electric Oven'}
    db.InsertDictionary("AllPropertyRecords", dict)
'''