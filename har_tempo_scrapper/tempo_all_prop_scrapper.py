import urllib
import urllib.request
from urllib.error import URLError, HTTPError
import os
from io import StringIO
import sys
import time
import datetime
import calendar
import random
import DBLib
import traceback
import Logger
'''
cases:
http error --> try again for a few times
data base connection error --> quit
program too many records --> reduce time span and try again
'''

def scrapZip(db, zip, propertyType, dateRangeStart, dateRangeEnd):
    nMonthSpan = 12 #the default number of months span
    datTo = dateRangeStart - datetime.timedelta(days=1)
    nTotalRetry = 5
    nRetryCnt =0
    bRollback = False
    bTryAgain = False
    while True:
        if bTryAgain == False:
            if bRollback == False:
                datFrom = datTo + datetime.timedelta(days=1)
                datTo = min(add_months(datFrom, nMonthSpan) - datetime.timedelta(days=1), dateRangeEnd)
            else:
                datTo = min(add_months(datFrom, nMonthSpan) - datetime.timedelta(days=1), dateRangeEnd)
                bRollback = False
        print("Working on {0} between {1} and {2}".format(zip, datFrom, datTo))
        #scrapResult = scrap_history(zip, propertyType, datFrom.strftime("%m/%d/%Y"), datTo.strftime("%m/%d/%Y"))#, "Both" )
        scrapResult = scrap_tempo_history(db, propertyType, datFrom, datTo, zip)
        nTotRec = scrapResult[2]
        strResult = scrapResult[0]
        strErrMsg = scrapResult[3]
        if strResult == "Fail":
            #quit the program
            Logger.appendToLogFile(0, strErrMsg)
            exit(-1)
        elif strResult == "Error":
            if strErrMsg == "Too many records returned":
                nRetryCnt = 0
                bTryAgain = False
                nMonthSpan = int(nMonthSpan / 2)
                bRollback = True
            else:
                bTryAgain = True
                nRetryCnt +=1
                if nRetryCnt > nTotalRetry:
                    print('retried a few times with no luck. Quit')
                    exit (-1)
        elif strResult == "Success":
            bTryAgain = False
            nRetryCnt = 0
            if nTotRec >=0 and nTotRec   < 10:
                # increase the month span to a large number
                nMonthSpan = 100
            elif nTotRec<=50 and nTotRec >=0:
                nMonthSpan = 60
            elif nTotRec <=600:
                nMonthSpan = int(1200/nTotRec*nMonthSpan)
            if nMonthSpan < 3:
                nMOnthSpan=3
            if nMonthSpan > 120:
                nMonthSpan = 120

            if bRollback == False and datTo == dateRangeEnd:
                break

        time.sleep(random.randint(3,10))
    return(True)
'''
    return value tuple: (Result,  Processed records, total records, (optional) ErrorMessage)
    Result: 
    "Fail": an error that deems quitting the program
    "Error": Encountered error, but remediable
    "Success" Successful 
    
'''
def scrap_tempo_history(db, property_type, startDate, endDate, zip):


    fakeTimeStamp = datetime.datetime.now() - datetime.timedelta(seconds=10)
    print(fakeTimeStamp.strftime("%m/%d/%Y %I:%M:%S %p"))
    cookiestr = "TempoCookie=Theme=Tempo; ASPSESSIONIDQCRASASB=NIMHDNLBKPDHCPFCGPHJAADD; ASPSESSIONIDCSQBTCRB=MCJCPOLBCDDKNCHPJODLJNAC; ASPSESSIONIDSQSDRBRA=NODALAMBJPBCGLGECJOJEEFL; ASPSESSIONIDQQQQTTBB=MNCODDCCGACGIKMMMAEFADLH; ASPSESSIONIDSCBDSACT=AFGEKMMCGBFLNJNIEOLEFAIE; ASPSESSIONIDQCDCQACQ=KHCAHLMCEJAALMIBOFCLHMDC; ASPSESSIONIDSSACDTTS=PLPAEFHDLABKBEIKALIJIIFM; ASPSESSIONIDQQADSDAD=HNPPKHAAHLEPMMNAJJLHDNJO; ASPSESSIONIDSQCSCABS=LMCFEJKBHBGLLIJPBGOPILFF; MLPData=MLPTicket=&IsMLPPassKey=false; testcookies=nothing; LastUser=xtan; .TAuth=B40EA55F39A8C16D98E2BBA2F439590928A264618150A746E1FC0F239D6FC9F517F2FFDBE845BD9B8FFA66022160F13635BBDCA01C2A9E6958A0941ADE031D2FDA66E790F38519C74559C1BE52C7CCA2EC97477944BAC388CD06E4ACB2E60AAB944EFDD5; ASPSESSIONIDSCDRCTAT=FELMOADCDLFAAAEEEAFOKKFG; ASPSESSIONIDCCDSCRCT=CNNAGPCCFEMKOBNFLPIONIJM; Sidebar_Collapsed=1; LastActivity={0}".format(
        fakeTimeStamp.strftime("%m/%d/%Y %I:%M:%S %p"))
    url = 'http://www.harmls.com/thirdparty/Scripts/GetData.asp'
    query_string = "((liststatus='closd'%20and%20ClosedDate%3E=convert(datetime,'{0}')%20AND%20ClosedDate%3C=convert(datetime,'{1}')))%20AND%20(ZipCode%20Like%20'{2}%25'%20)".format(
        startDate.strftime("%m/%d/%Y"), endDate.strftime("%m/%d/%Y"), zip)
    print(query_string)
    temp_data_file_path = "Files"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '734',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookiestr,
        'Host': 'www.harmls.com',
        'Upgrade-Insecure-Requests': '1'
    }
    data = {
        "appMinorVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "appVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Name": "3RDPARTY",
        "Pass": "DHA0ATFA",
        "Custom": "ALL",
        "Num": "1500",
        "Join": "",
        "Tbl": property_type,
        "Where": query_string,
        "ColumnHeader": "Y",
        "ItemList": "",
        "Format": "0",
        "Tax": "undefined",
        "DownloadDecodeOverride": "",
        "preventDecodeList": "",
        "D1SelectedIndex": "0",
        "NumberOfProperties": "1500",
        "D1": "ALL"
    }
    data = urllib.parse.urlencode(data)
    data = data.encode('ascii')
    req = urllib.request.Request(url, data=data, headers=headers)
    datS = datetime.datetime.now()
    try:
        print("Start request")
        response = urllib.request.urlopen(req)
    except:
        #hit a http error, will try again
        return ("Error",0,0, "Http request failed")
    print("Response received")
    responseBody = response.read()
    # now need to analyze if response is in bytes or not.
    # if it's in bytes, it's good data, otherwise there is something wrong in the request
    strResponse = responseBody.decode('utf_8', 'backslashreplace')
    #here test if the response is legimite
    if len(strResponse) < 200:
        if (strResponse.find('BAD USERNAME or PASSWORD') > 0):
            print("Bad user name/ password")
            return ("Fail", 0, 0, 'Bad user name/ password')
        else:
            return ("Fail", 0, 0, 'Unknown http error')
    # if success, write result to a stringIO object
    nRecCnt = strResponse.count("\n")
    print("{0} records are stripped".format(nRecCnt - 1))
    if nRecCnt >= 1500:
        return ("Error", 0, nRecCnt, "Too many records returned")
    strIO = StringIO(strResponse)
    temp_data_file_path = 'c:\\temp'
    targetFilePath = temp_data_file_path + "\{0}_{1}_{2}.dat".format(property_type, zip, startDate.strftime("%Y_%m_%d"))
    try:
        os.remove(targetFilePath)
    except OSError:
        pass
    f = open(targetFilePath, "w")
    # strResponseBody = byteResponseBody.decode('utf_8')
    # strResponseBody = binascii.
    f.write(strResponse)
    f.close()

    nRecProcessed = db.insertHarTempoRecords(strIO)
    datE = datetime.datetime.now()
    db.InsertOne("JobLog", ["zip", "PropType", "DateFrom", "DateTo", "TotalRec", "RecCnt", "JobStartTime", "JobEndTime", "Result"], [zip, property_type, startDate, endDate, nRecCnt, nRecProcessed, datS, datE, "Success"])
    return ("Success", nRecProcessed, nRecCnt, None)


'''
zip: zip code (string)
property_type: type of property, (string) e.g. "rnt" for rent, "res" for normal sales
startDate: start date mm/dd/yyyy, (string)
endDate: end date mm/dd/yyyy, (string)
'''
def obselete_scrap_history(zip, property_type, startDate, endDate, WriteToFile="" ):
    db = oMySql.ModuleMySql('73.136.184.214', 3306, 'xiaowei', 'Hhxxttxs2017', 'HARHistory')
    JobStartTime = datetime.datetime.now()
    tStart = datetime.datetime.now()
    fakeTimeStamp =  datetime.datetime.now()-datetime.timedelta(seconds=10)
    print(fakeTimeStamp.strftime("%m/%d/%Y %I:%M:%S %p"))
    cookiestr = "TempoCookie=Theme=Tempo; ASPSESSIONIDQCRASASB=NIMHDNLBKPDHCPFCGPHJAADD; ASPSESSIONIDCSQBTCRB=MCJCPOLBCDDKNCHPJODLJNAC; ASPSESSIONIDSQSDRBRA=NODALAMBJPBCGLGECJOJEEFL; ASPSESSIONIDQQQQTTBB=MNCODDCCGACGIKMMMAEFADLH; ASPSESSIONIDSCBDSACT=AFGEKMMCGBFLNJNIEOLEFAIE; ASPSESSIONIDQCDCQACQ=KHCAHLMCEJAALMIBOFCLHMDC; ASPSESSIONIDSSACDTTS=PLPAEFHDLABKBEIKALIJIIFM; ASPSESSIONIDQQADSDAD=HNPPKHAAHLEPMMNAJJLHDNJO; ASPSESSIONIDSQCSCABS=LMCFEJKBHBGLLIJPBGOPILFF; MLPData=MLPTicket=&IsMLPPassKey=false; testcookies=nothing; LastUser=xtan; .TAuth=B40EA55F39A8C16D98E2BBA2F439590928A264618150A746E1FC0F239D6FC9F517F2FFDBE845BD9B8FFA66022160F13635BBDCA01C2A9E6958A0941ADE031D2FDA66E790F38519C74559C1BE52C7CCA2EC97477944BAC388CD06E4ACB2E60AAB944EFDD5; ASPSESSIONIDSCDRCTAT=FELMOADCDLFAAAEEEAFOKKFG; ASPSESSIONIDCCDSCRCT=CNNAGPCCFEMKOBNFLPIONIJM; Sidebar_Collapsed=1; LastActivity={0}".format(fakeTimeStamp.strftime("%m/%d/%Y %I:%M:%S %p"))
    url = 'http://www.harmls.com/thirdparty/Scripts/GetData.asp'
    query_string = "((liststatus='closd'%20and%20ClosedDate%3E=convert(datetime,'{0}')%20AND%20ClosedDate%3C=convert(datetime,'{1}')))%20AND%20(ZipCode%20Like%20'{2}%25'%20)".format(startDate, endDate, zip)
    print(query_string)
    temp_data_file_path = "Files"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '734',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookiestr,
        'Host': 'www.harmls.com',
        'Upgrade-Insecure-Requests': '1'
        }
    data = {
        "appMinorVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "appVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Name": "3RDPARTY",
        "Pass": "DHA0ATFA",
        "Custom": "ALL",
        "Num": "1500",
        "Join": "",
        "Tbl": property_type,
        "Where": query_string,
        "ColumnHeader": "Y",
        "ItemList": "",
        "Format": "0",
        "Tax": "undefined",
        "DownloadDecodeOverride": "",
        "preventDecodeList": "",
        "D1SelectedIndex": "0",
        "NumberOfProperties": "1500",
        "D1": "ALL"
    }
    data = urllib.parse.urlencode(data)
    data = data.encode('ascii')
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        print("Start request")
        response = urllib.request.urlopen(req)
        print("Response received")
        responseBody = response.read()
        #now need to analyze if response is in bytes or not.
        #if it's in bytes, it's good data, otherwise there is something wrong in the request
        strResponse = responseBody.decode('utf_8', 'backslashreplace')

        if len(strResponse) < 200:
            if (strResponse.find( 'BAD USERNAME or PASSWORD')>0):
                return (False, "Bad username/password", -1)
            else:
                return (False, strResponse, -1)
        #if success, write result to a stringIO object
        nRecCnt = strResponse.count("\n")
        print("{0} records are stripped".format(nRecCnt-1))
        if nRecCnt >=1500:
            return (True, "Record count over 1500", nRecCnt)
        if WriteToFile=="Yes" or WriteToFile=="Both":
            targetFilePath = temp_data_file_path + "\{0}_{1}.dat".format(zip, startDate.replace("/","_"))
            try:
                os.remove(targetFilePath)
            except OSError:
                pass
            f = open(targetFilePath, "w")
            #strResponseBody = byteResponseBody.decode('utf_8')
            #strResponseBody = binascii.
            f.write(strResponse)
            f.close()
            print("data saved to file")
            #return (True, temp_data_file_path, nRecCnt)
            JobEndTime = datetime.datetime.now()
        if WriteToFile == "" or WriteToFile== "Both":
            strIO = StringIO(strResponse)
            writeResult = db.WriteHistoryData(strIO, property_type)
            tEnd = datetime.datetime.now()
            nElapsed = tEnd-tStart
            JobEndTime = datetime.datetime.now()
            if writeResult[0]:
                print("Data written successfully")
                #db.LogTransaction(startDate, endDate, zip, property_type, nRecCnt, nElapsed.seconds, 1, writeResult[1])
                db.logJobLog(zip, property_type, datetime.datetime.strptime(startDate, "%m/%d/%Y"), datetime.datetime.strptime(endDate, "%m/%d/%Y"), nRecCnt, JobStartTime, JobEndTime, 'success', writeResult[1])
            else:
                print("error write to DB")
                #db.LogTransaction(startDate, endDate, zip, property_type, nRecCnt, nElapsed.seconds, 1, writeResult[1])
                db.logJobLog(zip, property_type, datetime.datetime.strptime(startDate, "%m/%d/%Y"), datetime.datetime.strptime(endDate, "%m/%d/%Y"), nRecCnt, JobStartTime, JobEndTime, 'fail', writeResult[1])
        return (True, "file succesfully written", nRecCnt-1)
    except HTTPError as e:
        print(e.code)
        return (False, e.code, -1)
    except URLError as e:
        print(e.reason)
        return (False, e.reason, -1)
    except:
        print(sys.exc_info())
        return (False, "", -1)


def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

if __name__== "__main__":
    datStart = datetime.date(2001,1,1)
    datEnd=datetime.date(2017, 6, 1)
    #scrap_tempo_history('lnd', datStart, datEnd, '77096')
    try:
        print("connecting to db")
        #db = DBLib.db_mysql('73.136.184.214', 3306, 'xiaowei', 'Hhxxttxs2017', 'RealAnalysis')
        db = DBLib.db_mysql('10.10.1.48', 3306, 'xiaowei', 'Hhxxttxs2017', 'RealAnalysis')
        print("db connected")
        # db = DBLib.db_mysql('10.10.1.48', 3306, 'xiaowei', 'Hhxxttxs2017', 'RealAnalysis')
        #db = DBLib.db_mysql('localhost', 3306, 'root', 'thinkpad', 'RealAnalysis')
        # db = DBLib.db_mysql("10.10.1.48", 3306, 'xiaowei', 'Hhxxttxs2017', 'RealAnalysis')
        scrapZip(db, '77007', 'res', datStart, datEnd)
        scrapZip(db, '77007', 'rnt', datStart, datEnd)
        scrapZip(db, '77007', 'cnd', datStart, datEnd)
        scrapZip(db, '77007', 'lnd', datStart, datEnd)
    except:
        print(traceback.print_exc())

