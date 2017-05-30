#class library for MS Access related functions


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

    def InsertMany(self, strTable, lstColumns, lstValues):
        sql = self.prepareInsertSQL(strTable, lstColumns)
        self._cursor.executemany(sql, lstValues)
        self._conn.commit()

    def InsertOne(self, strTable, lstColumns, lstValues):
        sql = self.prepareInsertSQL(strTable, lstColumns)
        self._cursor.execute(sql, lstValues)

    def Committ(self):
        self._conn.commit()

    def prepareInsertSQL(self, strTable, lstColumns):
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(strTable, ",".join(lstColumns),",".join(['?'] * len(lstColumns)))
        return sql

    def InsertDictionary(self, strTableName, dict):
        lstColumns = list(dict.keys())
        lstValues = list(dict.values())
        self.InsertOne(strTableName, lstColumns, lstValues)

    '''
    here keys is a list of keys used in where statement 
    '''
    def UpdateDictionary(self, strTableName, dict, keys):
        #first pop the elements from the keys