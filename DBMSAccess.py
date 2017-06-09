#class library for MS Access related functions

import traceback
import pyodbc
class MSAccess:
    def __init__(self, strPath):
        self._db_file = strPath
        self._user = 'admin'
        self._password = ''
        if strPath[-3:] == 'mdb':
            odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;UID=%s;PWD=%s' % (self._db_file,self._user, self._password)
        else: # Or, for newer versions of the Access drivers:
            odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % (self._db_file,self._user, self._password)

        self._conn = pyodbc.connect(odbc_conn_str)
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
        cols = '=?'.join(lstColumnsToUpdate) + '=?'
        keys = '=? and '.join(lstKeysToUpdate) + '=?'
        sql = "UPDATE {0} SET {1} WHERE {2}".format(strTable, cols, keys)
        print(sql)
        return sql

    def prepareInsertSQL(self, strTable, lstColumns):
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(strTable, ",".join(lstColumns),",".join(['?'] * len(lstColumns)))
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
        print (sql)
        try:
            rslt = self._cursor.execute(sql, lstValuesToUpdate + lstKeyValues)
            if bAutoCommit:
                self._conn.commit()
            return rslt.rowcount
        except:
            print(traceback.print_exc())
            return 0