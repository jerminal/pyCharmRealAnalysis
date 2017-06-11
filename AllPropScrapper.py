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
import DBMSAccess
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

def scrapSoldProperties(datFrom, datTo, nJobId):
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

    #elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.LINK_TEXT, "Enter Matrix MLS")))
    (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "link_text", "Enter Matrix MLS")
    window_before = driver.window_handles[0]
    xpath = "/html[@class='wf-effra-n4-active wf-effra-n7-active wf-effra-n3-active wf-effra-n5-active wf-effra-n9-active wf-active']/body/div[@class='content overlay']/div[@class='container']/div[@class='rightPane']/div[@class='box_simple gray agentbox newhar']/div[@class='box_content grid_view']/a[1]"
    #elemNextLnk = driver.find_element_by_xpath(xpath)
    (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "xpath", xpath, True)
    #elemNextLnk.click()
    # switch to the new window, and click on "new listing"
    wait_for_new_window(driver)
    window_after = driver.window_handles[1]
    driver.close()
    driver.switch_to.window(window_after)
    strPartialText = "New Listing ("
    #elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, strPartialText)))
    (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "partial_link_text", strPartialText)
    driver.get(strEntryUrl)

    xpChkActive = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[2]/td[1]/div/input[@class='checkbox']"
    xpChkOptionPending = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[3]/td[1]/div/input[@class='checkbox']"
    xpChkPendConToShow = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[4]/td[1]/div/input[@class='checkbox']"
    xpChkPending = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[5]/td[1]/div/input[@class='checkbox']"
    xpChkSold = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[6]/td[1]/div/input[@class='checkbox']"
    xpChkWithdrawn = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[7]/td[1]/div/input[@class='checkbox']"
    xpChkExpired = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[8]/td[1]/div/input[@class='checkbox']"
    xpChkTerminated = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[9]/td[1]/div/input[@class='checkbox']"
    xpResults = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='ctl12']/table[@class='buttonBar']/tbody/tr/td[@class='link important barleft'][2]/a[@id='m_ucSearchButtons_m_lbSearch']/span[@class='linkIcon icon_default']"

    #make sure the page is loaded
    elemActive = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpChkActive)))
    elemOptionPending = driver.find_element_by_xpath(xpChkOptionPending)
    elemPendConToShow = driver.find_element_by_xpath(xpChkPendConToShow)
    elemPending = driver.find_element_by_xpath(xpChkPending)
    elemSold = driver.find_element_by_xpath(xpChkSold)
    elemWithdrawn = driver.find_element_by_xpath(xpChkWithdrawn)
    elemExpired = driver.find_element_by_xpath(xpChkExpired)
    elemTerminated = driver.find_element_by_xpath(xpChkTerminated)
    elemResults = driver.find_element_by_xpath(xpResults)

    #now uncheck Active, Optionpending, etc, and only check Sold Check box
    if elemActive.is_selected():
        elemActive.click()
    if elemOptionPending.is_selected():
        elemOptionPending.click()
    if elemPendConToShow.is_selected():
        elemPendConToShow.click()
    if elemPending.is_selected():
        elemPending.click()
    if not elemSold.is_selected():
        elemSold.click()
    #now set date range

    strDateRange = datFrom.strftime("%m/%d/%Y") + "-" + datTo.strftime("%m/%d/%Y")
    xpSoldDateRange = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[6]/td[2]/input[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']"
    elemSoldDateRange = driver.find_element_by_xpath(xpSoldDateRange)
    elemSoldDateRange.clear()
    elemSoldDateRange.send_keys(strDateRange)
    #now click to load the result pages
    elemResults.click()
    # now the new listing page is being loaded
    #below is the xpath to the total # of records
    xpTotalRecCount = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerLeft hideOnMap hideOnSearch hideNoResults']/span[@id='m_lblPagingSummary']/b[3]"
    #elemRecCnt = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpTotalRecCount)))
    (elemRecCnt, nFailureCnt) = find_wait_get_element(driver, "xpath", xpTotalRecCount)
    try:
        nRecCnt = int(elemRecCnt.text)
    except:
        #TODO: some work to do when the number of records returned >5000
        print('exception!')

    # now click the first listing in the list
    xpathFirstMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/table[@class='displayGrid nonresponsive ajax_display d1m_show']/tbody/tr[@id='wrapperTable'][1]/td[@class='d1m5']/span[@class='d1m1']/a"
    nCntTries = 0
    (elemFirstMLS, nFailureCnt) = find_wait_get_element(driver, "xpath", xpathFirstMLS)
    sMLS = elemFirstMLS.text
    (elemFirstMLS, nFailureCnt) = find_wait_get_element(driver, "xpath", xpathFirstMLS, True)
    '''
    while nCntTries<3:
        try:
            #elemFirstMLS = driver.find_element_by_xpath(xpathFirstMLS)
            (elemFirstMLS, nFailureCnt) = find_wait_get_element(driver, "xpath", xpathFirstMLS)
            sMLS = elemFirstMLS.text
            elemFirstMLS.click()
            break
        except:
            driver.refresh()
            nCntTries+=1
    '''
    # wait for the details page to load
    # xPathMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/div[@class='multiLineDisplay ajax_display d3m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d3m1']/span[@class='display']/table[@class='d3m2']/tbody/tr[2]/td[@class='d3m3']/span[@class='formula']/div[@class='multiLineDisplay ajax_display d48m_show nonresponsive']/table[@id='wrapperTable']/tbody/tr/td[@class='d48m1']/span[@class='display']/table[@class='d48m2']/tbody/tr[3]/td[@class='d48m5']/table[@class='d48m7']/tbody/tr[@class='d48m8']/td[@class='d48m16']/table[@class='d48m17']/tbody/tr[3]/td[@class='d48m19']/span[@class='wrapped-field']"
    xPathNext = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerLeft hideOnMap hideOnSearch hideNoResults']/span[@id='m_lblPagingSummary']/span[@class='pagingLinks']/a[@id='m_DisplayCore_dpy3']"
    NextLinkId = 'm_DisplayCore_dpy3'
    nExceptionCount = 0
    lstScrapResults = []
    nTotalCount = 0
    #now iterate through all the deails pages
    db = DBMSAccess.MSAccess(r"c:/temp/RealAnalysis.accdb")
    while nTotalCount < nRecCnt - 1:

        print("Rec {0} of {1}".format(nTotalCount+1, nRecCnt))
        #time.sleep(1)
        #while True:
        #nCntTries = 0
        (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "id", NextLinkId, True)
        if elemNextLnk is None:
            return (0,0)
        '''
        try:
            elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, NextLinkId)))
            break
        except:
            if nCntTries < 3:
                driver.refresh()
            else:
                print("encountered error while trying to click the next link")
                exit()
            nCntTries +=1
        '''
        #get the transaction type (rental, residental, etc)
        #xpTransType = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/div[@class='multiLineDisplay ajax_display d3m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d3m1']/span[@class='display']/table[@class='d3m2']/tbody/tr[2]/td[@class='d3m3']/span[@class='formula']/div[@class='multiLineDisplay ajax_display d82m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d82m1']/span[@class='display']/table[@class='d82m2']/tbody/tr[3]/td[@class='d82m5']/table[@class='d82m7']/tbody/tr[@class='d82m8']/td[@class='d82m15']/table[@class='d82m16']/tbody/tr[@class='d82m24'][1]/td[@class='d82m25']/span[@class='field d82m26']"
        #elemTransType = driver.find_element_by_xpath(xpTransType)
        #strTransType = elemTransType.text
        pageSource = driver.page_source
        #now get the lat/lon:
        #first the the current window handle
        mainWindow = driver.window_handles[0]
        #next trigger the new map view window
        #elemViewMap = driver.find_element_by_xpath('//*[@title="View Map"]')
        (elemViewMap, temp) = find_wait_get_element(driver, "xpath", '//*[@title="View Map"]', True)
        if not elemViewMap is None:
            #elemViewMap.click()
            #switch to the map view window
            wait_for_new_window(driver)
            mapWindow = driver.window_handles[1]
            driver.switch_to.window(mapWindow)
            #look for the tag with id: m_ucStreetViewService_m_hfParams
            tagId = "m_ucStreetViewService_m_hfParams"
            #elemLatLon = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, tagId)))
            (elemLatLon, temp) = find_wait_get_element(driver, "id", tagId)
            #elemLatLon = driver.find_element_by_id(tagId)
            #strip lat/lon:
            tagText = str(elemLatLon.get_attribute("value"))
            (lat, lon) = tagText.split("$")[1:3]
            driver.close()
            driver.switch_to.window(mainWindow)
            bNeedToRefreshNext = False
        else:
            (lat, lon) = (None, None)
            bNeedToRefreshNext = True
        #switch back to the original window

        dictPageResult = PropScrap.parseDetails(pageSource)
        if dictPageResult is not None:
            dictPageResult["Latitude"] = lat
            dictPageResult["Longitude"] = lon
            nMLSNum = dictPageResult['MLSNum']
            if nMLSNum is not None:
                lstScrapResults.append(dictPageResult)
                if db.InsertDictionary("AllPropertyRecords",dictPageResult) == 0:
                    #if insertion fails:
                    print("insertion failed. record: {0}".format(str(dictPageResult)))
                    appendToCSV(nJobId, nMLSNum, str(dictPageResult))
                else:
                    db.UpdateTable("AllPropertyRecords", ["LastUpdate", "FK_JobId"], [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nJobId], ["MLSNum"], [int(nMLSNum)], False)
                db.Committ()
        #if bNeedToRefreshNext or nFailureCnt>0:
        #    elemNextLnk = find_wait_get_element(driver, "id", NextLinkId)

        #elemNextLnk.click()
        (elemNextLnk, nFailureCnt) = find_wait_get_element(driver, "id", NextLinkId, True)
        nTotalCount +=1

    writeToCSV(lstScrapResults)
    driver.quit()
    return (nTotalCount, nRecCnt)

if __name__ == "__main__":
    db = DBMSAccess.MSAccess(r"c:/temp/RealAnalysis.accdb")
    sql = "SELECT JobId, DateFrom, DateTo FROM JobLog WHERE Status is null"
    db._cursor.execute(sql)
    #rToProcess = db._cursor.fetchone()
    rows = db._cursor.fetchall()
    for rToProcess in rows:
        datEnd = rToProcess.DateTo
        datStart = rToProcess.DateFrom
        nJobId = rToProcess.JobId
        tStart = datetime.datetime.now()
        db.UpdateTable("JobLog",["JobStartTime", "Status"], [tStart.strftime("%Y-%m-%d %H:%M:%S"), "WIP"], ["JobId"], [nJobId])

        #datEnd = datetime.date.today()
        #datStart = datEnd + datetime.timedelta(days=-6)
        (nProcessed, nTotal) = scrapSoldProperties(datStart, datEnd, nJobId)
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
