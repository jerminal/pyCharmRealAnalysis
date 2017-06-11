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
        cols = '=?, '.join(lstColumnsToUpdate) + '=?'
        keys = '=? and '.join(lstKeysToUpdate) + '=?'
        sql = "UPDATE {0} SET {1} WHERE {2}".format(strTable, cols, keys)
        #print(sql)
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
        #print (sql)
        try:
            rslt = self._cursor.execute(sql, lstValuesToUpdate + lstKeyValues)
            if bAutoCommit:
                self._conn.commit()
            return rslt.rowcount
        except:
            print(traceback.print_exc())
            return 0


if __name__ == "__main__":
    db = MSAccess(r"c:/temp/RealAnalysis.accdb")
    dict = {'ListAgentId': 'worker', 'CompBuyerAgent': None, 'Area': '9', 'ListBroker': 'HORE01/Homestead Realty', 'MarketArea': 'Heights/Greater Heights', 'CloseAgtTRECId': '0391794', 'YearBuilt': 1920, 'Heat': 'Central Gas', 'Baths': '2/0', 'Roof': None, 'LPperSqft': 1.29, 'PendingDate': '12/20/2015', 'LeasedPricePerSqft': 1.24, 'SchoolDistrict': '27 - Houston', 'Flooring': 'Wood', 'TaxID': '021-018-000-0030', 'SaleMLSNum': None, 'MasterBath': None, 'LotSize': 8180, 'Address': '533 Oxford Street', 'OrigPrice': None, 'LeaseAlso': None, 'AgentPhone': None, 'LotDesc': 'Other', 'HighSchool': 'HEIGHTS HIGH SCHOOL', 'UnitLevel': None, 'ListDate': '12/20/2015', 'ListAgentName': 'Kim Pedigo', 'TaxRate': None, 'Foundation': None, 'Latitude': '29.781141', 'PropertyType': 'Rental', 'BrokerAddress': 'PO Box 130385, Houston               TX 77219', 'AgentEmail': None, 'Interior': None, 'Subdivision': 'Houston Heights', 'ListPrice': 2300.0, 'CompSubAgent': None, 'WaterfrontFeat': None, 'LeaseDate': '01/01/2016', 'TotalDiscount': None, 'ApprovalRequirement': 'Yes/Good job, good credit.', 'City': 'Houston', 'Heating': 'Central Gas', 'ApplicationFee': 55.0, 'MaintFee': None, 'Countertops': 'Tiles', 'Status': 'Sold', 'TotalUnits': None, 'UnitStories': '1', 'Bonus': None, 'Longitude': '-95.392221', 'Restrictions': 'No Restrictions', 'CloseAgentId': 'WORKER', 'ListAgent': 'worker/Kim Pedigo', 'Range': 'Electric Cooktop', 'LegalDesc': 'TRS 1A 2A & 3 BLK 286 HOUSTON HEIGHTS', 'County': 'Harris', 'ListBrokerName': 'Homestead Realty', 'Stories': None, 'TDate': '12/20/2015', 'FloorLocation': None, 'Zip': '77007 - 2601', 'PropertyClass': 'Single Family Detached', 'MLSNum': '77163257', 'DateAvail': '10/23/2015', 'Access': None, 'CloseBroker': 'Homestead Realty (HORE01)', 'Style': None, 'EstCloseDate': '01/01/2016', 'CloseAgentName': 'Kim Pedigo ', 'LotValue': None, 'Acres': '/ 0 Up To 1/4 Acre', 'ListBrokerId': 'HORE01', 'Builder': None, 'MiddleSchool': 'HOGG MIDDLE SCHOOL (HOUSTON)', 'ExteriorCons': None, 'Type': None, 'LeasePrice': 2200.0, 'Cooling': 'Central Electric', 'PrivatePool': 'No', 'Location': None, 'Bedrooms': '3/', 'RentalTerm': 'One Year', 'State': 'Texas', 'BedroomsDesc': 'All Bedrooms Down', 'DaysOnMarket': '', 'CloseBrokerId': 'HORE01', 'CloseAgent': 'Kim Pedigo (WORKER)', 'SecurityDeposit': '2300', 'BldgSqft': 1780, 'MasterPlanned': None, 'LicensedSupervisor': None, 'Connections': None, 'PrvtPool': 'No', 'CloseBrokerName': 'Homestead Realty ', 'ElemSchool': 'HARVARD ELEMENTARY SCHOOL', 'Oven': 'Electric Oven'}
    db.InsertDictionary("AllPropertyRecords", dict)