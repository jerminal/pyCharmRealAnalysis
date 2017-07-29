from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import datetime
import csv
import DBMSAccess
import XmlConfigReader
import AllPropDetailPageScrapper as PropScrap
import traceback
import DBLib
import time

import os

def appendToCSV(nJObId, nMLS, msg):
    strLogFilePath = os.getcwd() + r'\errorLog.csv'
    with open(strLogFilePath, 'a') as f:
        wr = csv.writer(f, dialect= 'excel')
        wr.writerow((nJobId,)+  (nMLS, ) + (msg, ))
    f.close()

def writeToCSV(ary):
    (lstSectKeys, lstSectDict, dictSectionLookup) = PropScrap.readAllPropScrapperConfigSections()
    for idx, item in enumerate(lstSectDict):
        if idx >0:
            lstSectDict[0].update(item)
    header = list(lstSectDict[0].keys())

    #header = list(ary[0].keys())
    aryValues = []
    for item in ary:
        aryValues.append(list(item.values()))
    aryFileData = []
    for dict in ary:
        row = []
        for key in header:
            try:
                valCol = dict[key]
            except:
                valCol = None
            row.append(valCol)
        aryFileData.append(row)

    with open(r"c:\temp\outputraw.csv", 'w') as f:
        wr = csv.writer(f, dialect='excel')
        wr.writerow(header)
        wr.writerows(aryValues)
    with open(r"c:\temp\output.csv", 'w') as f:
        wr = csv.writer(f, dialect='excel')
        wr.writerow(header)
        wr.writerows(aryFileData)
    print('done')
'''
this procedure waits until new window opens
'''
def wait_for_new_window(driver, timeout=10):
    handles_before = driver.window_handles
    yield
    WebDriverWait(driver, timeout).until(
        lambda driver: len(handles_before) != len(driver.window_handles))
'''
find, wait and get element, if not successful, it will keep on trying for 10 times before quit the program
'''
def find_wait_get_element(driver, elementType, val, bClick = False):
    nFailureCount = 0
    while nFailureCount < 5:
        try:
            if elementType == "link_text":
                elem = elemNextLnk = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, val)))
            elif elementType == "xpath":
                elem = elemNextLnk = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, val)))
            elif elementType == "id":
                elem = elemNextLnk = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, val)))
            elif elementType == "partial_link_text":
                elem = elemNextLnk = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, val)))
            elif elementType == "name":
                elem = elemNextLnk = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, val)))
            else:
                elem = elemNextLnk = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, val)))
            if bClick:
                elem.click()
            return (elem, nFailureCount)
        except:
            nFailureCount +=1
            driver.refresh()
    return (None, nFailureCount)

def queryllPropClassicPage(driver, dictParams):
    #load all property search/classic screen
    lnkAllPropSearch='http://matrix.harmls.com/Matrix/Search/AllProperties/Classic'
    driver.get(lnkAllPropSearch)
    time.sleep(3)
    lstFormInputs = []

    #now check/uncheck the property status boxes, and set start/end date values
    xpChkActive = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[2]/td[1]/div/input[@class='checkbox']"
    xpChkOP = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[3]/td[1]/div/input[@class='checkbox']"
    xpChkPCS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[4]/td[1]/div/input[@class='checkbox']"
    xpChkPending = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[5]/td[1]/div/input[@class='checkbox']"
    xpChkSold = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[6]/td[1]/div/input[@class='checkbox']"
    xpInputActive = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[2]/td[2]/input[@id='FmFm1_Ctrl16_20915_Ctrl16_TB']"
    xpInputSold = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[6]/td[2]/input[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']"

    lstFormInputs.append((xpChkActive, 'CheckBox', True))
    lsttFormInputs.append((xpChkOp, 'CheckBox', True))
    lstFormInputs.append((xpChkPCS, 'CheckBox', True))
    lstFormInputs.append((xpChkPending,'CheckBox', True))

    elemActive = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpChkActive)))
    elemOptionPending = driver.find_element_by_xpath(xpChkOP)
    elemPendConToShow = driver.find_element_by_xpath(xpChkPCS)
    elemPending = driver.find_element_by_xpath(xpChkPending)
    elemSold = driver.find_element_by_xpath(xpChkSold)
    elemInputActive = driver.find_element_by_xpath(xpInputActive)
    elemInputSold = driver.find_element_by_xpath(xpInputSold)

    strDtRange = datFrom.strftime("%m/%d/%Y") + '-' + datTo.strftime("%m/%d/%Y")

    #now uncheck Active, Optionpending, etc, and only check Sold Check box
    #first uncheck everything
    if elemActive.is_selected() :
        elemActive.click()
    if elemOptionPending.is_selected():
        elemOptionPending.click()
    if elemPendConToShow.is_selected():
        elemPendConToShow.click()
    if elemPending.is_selected():
        elemPending.click()
    if elemSold.is_selected():
        elemSold.click()
    lstPropStat = strPropStat.split(',')
    for propStat in lstPropStat:
        if propStat == 'active':
            elemActive.click()
            elemInputActive.clear()
            elemInputActive.send_keys(strDtRange)
        elif propStat == 'sold':
            elemSold.click()
            elemInputSold.clear()
            elemInputSold.send_keys(strDtRange)

    #now select the property type
    xpPropTypeRes = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[1]"
    xpPropTypeCnd = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[2]"
    xpPropTypeLnd = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[3]"
    xpPropTypeRnt = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[5]"
    elemPTRes = driver.find_element_by_xpath(xpPropTypeRes)
    elemPTCnd = driver.find_element_by_xpath(xpPropTypeCnd)
    elemPTLnd = driver.find_element_by_xpath(xpPropTypeLnd)
    elemPTRnt = driver.find_element_by_xpath(xpPropTypeRnt)

    lstPropType = strPropType.split(',')
    for propType in lstPropType:
        if propType == 'res':
            elemPTRes.click()
        elif propType == 'cnd':
            elemPTCnd.click()
        elif propType == 'lnd':
            elemPTLnd.click()
        elif propType == 'rnt':
            elemPTRnt.click()
        else:
            continue
    xpResultLnk = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='ctl12']/table[@class='buttonBar']/tbody/tr/td[@class='link important barleft'][2]/a[@id='m_ucSearchButtons_m_lbSearch']/span[@class='linkIcon icon_default']"
    elemResultLnk = driver.find_element_by_xpath(xpResultLnk)
    elemResultLnk.click()
    time.sleep(2)


'''
strPropType: res, lnd, cnd, rnt
strPropStat: active, or, sold 
'''
def scrapAllProperties(db, datFrom, datTo, strPropType, strPropStat, nJobId):
    cfg = XmlConfigReader.Config("AllPropScrapper", "DEV")
    strUserName = cfg.getConfigValue("HARUserName")
    strPwd = cfg.getConfigValue("HARPassword")
    strEntryUrl = cfg.getConfigValue("EntryUrl")
    # strUrl = str(cfg.getConfigValue("EntryUrl"))

    executable_path = r'C:\Python35\selenium\webdriver\firefox\x86\geckodriver.exe'
    binary = FirefoxBinary('C:/Program Files (x86)/Mozilla Firefox/firefox.exe')
    driver = webdriver.Firefox(executable_path=executable_path)
    # driver = webdriver.Firefox(firefox_binary=binary)
    print(cfg.getConfigValue("EntryUrl"))
    driver.get(cfg.getConfigValue("StartingUrl"))  # load the web page

    # look for user name log in:
    elemUsr = driver.find_element_by_id("member_email")
    elemUsr.send_keys(strUserName)
    elemPwd = driver.find_element_by_id("member_pass")
    elemPwd.send_keys(strPwd)
    elemPwd.send_keys(Keys.RETURN)

    (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "link_text", "Enter Matrix MLS")
    window_before = driver.window_handles[0]
    xpath = "/html[@class='wf-effra-n4-active wf-effra-n7-active wf-effra-n3-active wf-effra-n5-active wf-effra-n9-active wf-active']/body/div[@class='content overlay']/div[@class='container']/div[@class='rightPane']/div[@class='box_simple gray agentbox newhar']/div[@class='box_content grid_view']/a[1]"
    (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "xpath", xpath, True)
    time.sleep(3)

    wait_for_new_window(driver)
    window_after = driver.window_handles[1]
    driver.close()
    driver.switch_to.window(window_after)


    queryllPropClassicPage(driver, dictFormInputs)

    #now the result page loads
    xpRecordCount = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerLeft hideOnMap hideOnSearch hideNoResults']/span[@id='m_lblPagingSummary']/b[3]"
    elemTotRecCnt = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpRecordCount)))
    try:
        nRecCnt = int(elemTotRecCnt.text)
    except:
        # TODO: some work to do when the number of records returned >5000
        print('exception!')

    # now click the first listing in the list
    xpathFirstMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/table[@class='displayGrid nonresponsive ajax_display d1m_show']/tbody/tr[@id='wrapperTable'][1]/td[@class='d1m5']/span[@class='d1m1']/a"
    nCntTries = 0
    (elemFirstMLS, nFailureCnt) = find_wait_get_element(driver, "xpath", xpathFirstMLS)
    sMLS = elemFirstMLS.text
    elemFirstMLS.click()
    NextLinkId = 'm_DisplayCore_dpy3'
    nTotalCount = 0
    lstScrapResults = []
    while nTotalCount < nRecCnt :
        print("Rec {0} of {1}".format(nTotalCount+1, nRecCnt))
        (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "id", NextLinkId, True)
        if elemNextLnk is None:
            return (0,0)
        pageSource = driver.page_source
        # now get the lat/lon:
        # first the the current window handle
        mainWindow = driver.window_handles[0]
        # next trigger the new map view window
        # elemViewMap = driver.find_element_by_xpath('//*[@title="View Map"]')
        (elemViewMap, temp) = find_wait_get_element(driver, "xpath", '//*[@title="View Map"]', True)
        if not elemViewMap is None:
            # switch to the map view window
            wait_for_new_window(driver)
            mapWindow = driver.window_handles[1]
            driver.switch_to.window(mapWindow)
            # look for the tag with id: m_ucStreetViewService_m_hfParams
            tagId = "m_ucStreetViewService_m_hfParams"
            # elemLatLon = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, tagId)))
            (elemLatLon, temp) = find_wait_get_element(driver, "id", tagId)
            # elemLatLon = driver.find_element_by_id(tagId)
            # strip lat/lon:
            tagText = str(elemLatLon.get_attribute("value"))
            (lat, lon) = tagText.split("$")[1:3]
            driver.close()
            driver.switch_to.window(mainWindow)
            bNeedToRefreshNext = False
        else:
            (lat, lon) = (None, None)
            bNeedToRefreshNext = True
        # switch back to the original window
        dictPageResult = PropScrap.parseDetails(pageSource)
        if dictPageResult is not None:
            dictPageResult["Latitude"] = lat
            dictPageResult["Longitude"] = lon
            nMLSNum = dictPageResult['MLSNum']
            if nMLSNum is not None:
                lstScrapResults.append(dictPageResult)
                if db.TransferDictionary("Matrix_AllPropRecords", dictPageResult) == 1:
                    nTotalCount += 1
                else:
                    # if insertion fails:
                    print("insertion failed. record: {0}".format(str(dictPageResult)))
                    appendToCSV(nJobId, nMLSNum, str(dictPageResult))
                    nTotalCount += 1

                    #db.updateRecord("Matrix_AllPropRecords", ["FK_JobId"],[nJobId], ["MLSNum"],[int(nMLSNum)], True)
                    #db.Committ()
        # if bNeedToRefreshNext or nFailureCnt>0:
        #    elemNextLnk = find_wait_get_element(driver, "id", NextLinkId)

        # elemNextLnk.click()
        #(elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "id", NextLinkId, True)


if __name__ == "__main__":
    cfg = XmlConfigReader.Config("AllPropScrapper", "DEV")
    host = cfg.getConfigValue(r'MySQL/host')
    #host = '73.136.184.214'
    port = int(cfg.getConfigValue(r"MySQL/port"))
    user = cfg.getConfigValue(r"MySQL/user")
    passwd = cfg.getConfigValue(r"MySQL/password")

    db = cfg.getConfigValue(r"MySQL/DB")
    #db = DBAccess('mysql', host=host, port=port, db_name =db, user_id = user, pwd = passwd)
    #db = DBMSAccess.MSAccess(r"c:/temp/RealAnalysis.accdb")
    db = DBLib.db_mysql(host, port, user, passwd, "RealAnalysis")
    #sql = "SELECT JobId, DateFrom, DateTo FROM JobLog WHERE Status is null"
    #db._cursor.execute(sql)

    datStart = datetime.date.today()
    datEnd = datetime.date.today()
    nJobId = 0
    (nProcessed, nTotal) = scrapAllProperties(db, datStart, datEnd, 'res', 'active', nJobId)
    '''    
    rows = db._cursor.fetchall()
    for rToProcess in rows:
        datEnd = rToProcess[2]
        datStart = rToProcess[1]
        nJobId = rToProcess[0]
        tStart = datetime.datetime.now()
        db.UpdateTable("JobLog",["JobStartTime", "Status"], [tStart.strftime("%Y-%m-%d %H:%M:%S"), "WIP"], ["JobId"], [nJobId])

        #datEnd = datetime.date.today()
        #datStart = datEnd + datetime.timedelta(days=-6)
        
        if nProcessed == 0:
            #the job failed
            tEnd = datetime.datetime.now()
            nDuration = (tEnd - tStart).seconds / 60
            db.UpdateTable("JobLog", ["JobStartTime", "Status", "Duration", "HARRecCnt","RecCnt"],
                           [tEnd.strftime("%Y-%m-%d %H:%M:%S"), "Fail", nDuration, nTotal, nProcessed], ["JobId"], [nJobId])
        else:
            tEnd = datetime.datetime.now()
            nDuration = (tEnd-tStart).seconds/60
            db.UpdateTable("JobLog", ["JobStartTime", "Status", "Duration", "HARRecCnt","RecCnt"],
                           [tEnd.strftime("%Y-%m-%d %H:%M:%S"), "Complete", nDuration, nTotal, nProcessed], ["JobId"],[nJobId])
    '''