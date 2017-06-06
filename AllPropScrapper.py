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

def writeToCSV(ary):
    dictColumns = {"MLSNum": "ML#: ", "Status": "Status: ", "ListPrice": "List Price: ", "Address": "Address: ",
                   "Area": "Area: ", "LPperSqft": "LP/SF: ", "TaxID": "Tax Acc #: ", "DaysOnMarket": "DOM: ",
                   "City": "City: ", "State": "State: ", "County": "County: ", "MasterPlanned": "Master Planned: ",
                   "Location": "Location:", "MarketArea": "Market Area:", "Subdivision": "Subdivision: ",
                   "SectionNum": "Secction #:", "LotSize": "Lot Size: ", "BldgSqft": "SqFt: ", "LotValue": "Lot Value:",
                   "LeaseAlso": "Lease Also:", "YearBuilt": "Year Built: ", "LegalDesc": "Legal Desc: ",
                   "ListBroker": "List Broker: ", "ListAgent": "List Agent: ", "BrokerAddress": "Address: ",
                   "LicensedSupervisor": "Licensed Supervisor:", "SchoolDistrict": "School District: ",
                   "ElemSchool": "Elem: ",
                   "MiddleSchool": "Middle: ", "HighSchool": "High: ", "Style": "Style: ", "Stories": "# Stories: ",
                   "Type": "Type: ", "Access": "Access: ", "Acres": "Acres: ", "Bedrooms": "Bedrooms: ",
                   "Baths": "Baths F/H: ",
                   "Builder": "Builder Nm: ", "Oven": "Oven:", "Roof": "Roof: ",
                   "Flooring": "Flooring: ", "Foundation": "Foundation: ", "Countertops": "Countertops: ",
                   "PrvtPool": "Prvt Pool:",
                   "WaterfrontFeat": "Waterfront Feat: ", "ListDate": "List Date: ", "MaintFee": "Maint. Fee: ",
                   "TaxRate": "Tax Rate: ", "Zip": "Zip Code: ", "AgentEmail": "Agent Email:",
                   "AgentPhone": "Agent Phone: ", "Connections": "Connect: ", "Interior": "Interior: ",
                   "MasterBath": "Master Bath: ",
                   "ExteriorCons": "Exterior Constr", "Range": "Range: ", "LotDesc": "Lot Description: ",
                   "Heating": "Heat: ",
                   "Cooling": "Cool: ", "BedroomsDesc": "Bedrooms: ",
                   "SellAgentTRECId": "TREC #: ", "SalePrice": "Sale Price: ", "CloseDate": "Close Date: ",
                   "SalePricePerSqft": "SP$/SF: ", "DaysToClose": "Days to Close: ", "FinTerms": "Terms:",
                   "AmortizeYears": "Amortize Years: ",
                   "NewLoan": "New Loan: ", "PendingDate": "Pending Date: ", "EstCloseDate": "Est Close Dt: ",
                   "CoOp": "CoOp: "
                   }
    header = []
    aryValues = []
    for key in dictColumns:
        header.append(key)
    aryValues.append(header)
    for row in ary:
        newRow = []
        for col in header:
            print(col)
            try:
                print(row[col])
                newRow.append(row[col])
            except:
                print('key {0} not found in result'.format(col))
                newRow.append(None)
        aryValues.append(newRow)
    with open(r"c:\temp\output.csv", 'w') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerows(aryValues)
    print('done')



if __name__ == "__main__":
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

    elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.LINK_TEXT, "Enter Matrix MLS")))
    window_before = driver.window_handles[0]
    xpath = "/html[@class='wf-effra-n4-active wf-effra-n7-active wf-effra-n3-active wf-effra-n5-active wf-effra-n9-active wf-active']/body/div[@class='content overlay']/div[@class='container']/div[@class='rightPane']/div[@class='box_simple gray agentbox newhar']/div[@class='box_content grid_view']/a[1]"
    elemNextLnk = driver.find_element_by_xpath(xpath)
    elemNextLnk.click()
    # switch to the new window, and click on "new listing"
    time.sleep(2)
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    strPartialText = "New Listing ("
    elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, strPartialText)))
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
    datEnd= datetime.date.today()
    datStart=datEnd + datetime.timedelta(days = -5)
    strDateRange = datStart.strftime("%m/%d/%Y") + "-" + datEnd.strftime("%m/%d/%Y")
    xpSoldDateRange = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[6]/td[2]/input[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']"
    elemSoldDateRange = driver.find_element_by_xpath(xpSoldDateRange)
    elemSoldDateRange.clear()
    elemSoldDateRange.send_keys(strDateRange)
    #now click to load the result pages
    elemResults.click()
    # now the new listing page is being loaded
    #below is the xpath to the total # of records
    xpTotalRecCount = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerLeft hideOnMap hideOnSearch hideNoResults']/span[@id='m_lblPagingSummary']/b[3]"
    elemRecCnt = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpTotalRecCount)))
    try:
        nRecCnt = int(elemRecCnt.text)
    except:
        #TODO: some work to do when the number of records returned >5000
        print('exception!')

    # now click the first listing in the list
    xpathFirstMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/table[@class='displayGrid nonresponsive ajax_display d1m_show']/tbody/tr[@id='wrapperTable'][1]/td[@class='d1m5']/span[@class='d1m1']/a"
    elemFirstMLS = driver.find_element_by_xpath(xpathFirstMLS)
    sMLS = elemFirstMLS.text
    elemFirstMLS.click()
    # wait for the details page to load
    # xPathMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/div[@class='multiLineDisplay ajax_display d3m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d3m1']/span[@class='display']/table[@class='d3m2']/tbody/tr[2]/td[@class='d3m3']/span[@class='formula']/div[@class='multiLineDisplay ajax_display d48m_show nonresponsive']/table[@id='wrapperTable']/tbody/tr/td[@class='d48m1']/span[@class='display']/table[@class='d48m2']/tbody/tr[3]/td[@class='d48m5']/table[@class='d48m7']/tbody/tr[@class='d48m8']/td[@class='d48m16']/table[@class='d48m17']/tbody/tr[3]/td[@class='d48m19']/span[@class='wrapped-field']"
    xPathNext = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerLeft hideOnMap hideOnSearch hideNoResults']/span[@id='m_lblPagingSummary']/span[@class='pagingLinks']/a[@id='m_DisplayCore_dpy3']"
    NextLinkId = 'm_DisplayCore_dpy3'
    nExceptionCount = 0
    lstScrapResults = []
    nTotalCount = 0
    #now iterate through all the deails pages
    while nTotalCount < nRecCnt - 1:
        try:
            elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, NextLinkId)))
            #get the transaction type (rental, residental, etc)
            xpTransType = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/div[@class='multiLineDisplay ajax_display d3m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d3m1']/span[@class='display']/table[@class='d3m2']/tbody/tr[2]/td[@class='d3m3']/span[@class='formula']/div[@class='multiLineDisplay ajax_display d82m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d82m1']/span[@class='display']/table[@class='d82m2']/tbody/tr[3]/td[@class='d82m5']/table[@class='d82m7']/tbody/tr[@class='d82m8']/td[@class='d82m15']/table[@class='d82m16']/tbody/tr[@class='d82m24'][1]/td[@class='d82m25']/span[@class='field d82m26']"
            elemTransType = driver.find_element_by_xpath(xpTransType)
            strTransType = elemTransType.text
            pageSource = driver.page_source

            dictPageResult = PropScrap.parseDetails(pageSource)
            lstScrapResults.append(dictPageResult)
            elemNextLnk.click()
            nTotalCount +=1
        except:
            traceback.print_exc()
            print('the next link is not found, it will try again')
            time.sleep(2)
