import pymysql
from functools import reduce
import traceback
import sys
import datetime
import dateutil.parser as dparser
from io import StringIO

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
        self._ColumnsList = temp
        #print( temp)
        return temp

    '''get the insert statement for a target table'''
    '''it retrieves all the columns of a table, and generate the sql insertion string'''
    def prepareInsertStatement(self, strTargetTable, lstColumns = None):
        if lstColumns is None:
            lstColumns = self.getColumnsList(strTargetTable)
            lstColumns = self._ColumnsList
        else:
            self._ColumnsList = lstColumns
        columnsList = reduce((lambda x, y: x + ', ' + y) , lstColumns)
        valueList = ["%s"]* len(lstColumns)
        valueList1 = reduce((lambda x,y: x + ', ' +y), valueList)
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(strTargetTable, columnsList, valueList1)
        print(sql)
        self._InsertSql = sql
        return sql

    '''
        prepare the update statement
    '''
    def prepareUpdateStatement(self, strTargetTable, lstColumns = None, keyColumns=None):
        if lstColumns is None:
            lstColumns = self.getColumnsList(strTargetTable)[:]
        for item in keyColumns:
            lstColumns.remove(item)
        lstValClause = '=%s, '.join(lstColumns) + '=%s'
        lstWhereClause = '=%s and '.join(keyColumns) + '=%s'
        sql = "UPDATE {0} SET {1} WHERE {2}".format(strTargetTable, lstValClause, lstWhereClause)
        self._updateSql = sql
        print(self._updateSql)

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
            print(data + whereData)
            self._cur.execute(self._updateSql,data + whereData)
        else:
            #it's a dictionary
            dict = {}
            for item in whereClauseColumns:
                dict[item] = data.pop(item)

        if bAutoCommit:
            self._conn.commit()
        return 1
    '''transfers one record contained in data row to target table
    difference between transfer and insert is transfer wraps around the insert, prepares the insert sql 
    and switch to update if insert causes a primary key violation
    '''

    def transferOneRecord(self, strTargetTable, dataRow, whereClauseColumns, bAutocommit = True):
        #self.prepareInsertStatement(strTargetTable)
        try:
            #first will try to insert the record
            result = self._cur.execute(self._InsertSql, dataRow)
            if bAutocommit:
                self._conn.commit()
            #print('1 row updated to mysql')
            return 1
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062: #it's a primary key error
                print(sys.exc_info())
                result = self.updateRecord(strTargetTable, dataRow, whereClauseColumns, bAutocommit)
                return result
            else:
                return 0

    '''
        insert the csv as sIO into AllPropertyRecords table
        the first row is the column names
    '''
    def insertHarTempoAllRecords(self, sIO):
        strTargetTable = 'HarTempo_AllRecords'
        nRowProcessed = 0
        lines = sIO.readlines()
        nRowCount = len(lines) - 1
        lines = [x.rstrip('\n') for x in lines]
        self._ColumnsList = lines[0]
        self._InsertSql = self.prepareInsertStatement(strTargetTable)

        for line in lines[1:]:
            dataRow = line.split(sep='\t')
            for idx, item in enumerate(dataRow):
                if len(item) == 0:
                    dataRow[idx] = None
                else:
                    #test if the item is a date type, if so, convert the format
                    try:
                        dt = dparser.parse(item, fuzzy=True)
                        if len(item) <= 10:
                            #this is a date
                            dataRow[idx] = dt.strftime("%Y-%m-%d")
                        elif len(item) <= 30:
                            #this is a date time
                            dataRow[idx] = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        continue
            rToInsert = tuple(dataRow)
            nRowProcessed += self.transferOneRecord(strTargetTable, rToInsert, ["MLSNum"])
        return nRowProcessed

    def obselete_WriteHistoryData(self, sIO, strType):
        #dateParse = lambda x: pd.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p') if len(x) > 10 else pd.datetime.strptime(x, '%m/%d/%Y')
        nTotRow = 0
        if strType == 'res':
            dateColumns = ['AuctionDate','BonusEndDate','ClosedDate','CompletedConstructionDate','CompletionDate','EstClosedDate','Modified','ListDate','OffMarketDate','OnlineBiddingDate','PendingDate','RemovalOptDate','TerminationDate','WithdrawnDate']
            strTableName = "residentialsaleshistory"
        elif strType == 'rnt':
            dateColumns=['BonusEndDate','ClosedDate','CompletionDate','DateAvail','EstClosedDate','ListDate','OffMarketDate','Modified','PendingDate','RemovalOptDate','TerminationDate','WithdrawnDate']
            strTableName = "rentalsaleshistory"
        else:
            return (False, "Type {0} is not recognized".format(strType))
        self.prepareInsertStatement(strTableName)

        lines = sIO.readlines()
        nRowCount = len(lines)
        lines = [x.rstrip('\n') for x in lines]
        for line in lines[1:]:
            data = line.split(sep='\t')
            for idx, item in enumerate(data):
                if item.count("/") == 2 and item[:4] != 'http':
                    if len(item) <= 10:
                        # it is a date
                        try:
                            data[idx] = datetime.datetime.strptime(item, "%m/%d/%Y").strftime("%Y-%m-%d")
                        except:
                            # do nothing here
                            print("fail to convert to date: {0}".format(item))
                    elif len(item) <= 30:
                        try:
                            # it is a datetime
                            data[idx] = datetime.datetime.strptime(item, "%m/%d/%Y %I:%M:%S %p").strftime(
                                "%Y-%m-%d %H:%M:%S")
                        except:
                            print("fail to convert to datetime: {0}".format(item))
                elif item == '':
                    data[idx] = None
            #print(data)
            dataRow = tuple(data)
            nTotRow += self.transferOneRecord(dataRow)

        '''
        dataF = pd.read_table(sIO, error_bad_lines=False, parse_dates=dateColumns, infer_datetime_format=True, warn_bad_lines=True)
        dataF1 = dataF.where((pd.notnull(dataF)), None)
        nRowCount = len(dataF1.index)
        # print(dataF.columns)
        for id, row in dataF1.iterrows():
            try:
                dataRow = tuple(dataF1.ix[id])
                self.transferOneRecord(dataRow)
                nTotRow +=1
            except:
                print(sys.exc_info())
                return (False, traceback.format_exc())
        '''
        print("{0}/{1} records updated".format(nTotRow, nRowCount))
        return (True, "{0}/{1} records updated".format(nTotRow, nRowCount))

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