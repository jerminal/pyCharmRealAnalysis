from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import csv
import DBMSAccess
import XmlConfigReader
import NewPropertyDetailPageScrapper as PropScrap
import datetime
import sys
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
                   "AgentPhone": "Agent Phone: ", "Connections": "Connect: ", "Interior": "Interior: ", "MasterBath": "Master Bath: ",
                    "ExteriorCons": "Exterior Constr", "Range": "Range: ", "LotDesc": "Lot Description: ", "Heating": "Heat: ",
                    "Cooling": "Cool: ", "BedroomsDesc": "Bedrooms: ",
                   "SellAgentTRECId": "TREC #: ", "SalePrice": "Sale Price: ", "CloseDate": "Close Date: ",
                   "SalePricePerSqft": "SP$/SF: ", "DaysToClose": "Days to Close: ", "FinTerms": "Terms:",
                   "AmortizeYears": "Amortize Years: ",
                   "NewLoan": "New Loan: ", "PendingDate": "Pending Date: ", "EstCloseDate": "Est Close Dt: ", "CoOp":"CoOp: "
    }
    header = []
    aryValues = []
    for key in dictColumns:
        header.append(key)
    aryValues.append(header)
    for row in ary:
        newRow =[]
        for col in header:
            print(col)
            try:
                #print(row[col])
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
    cfg = XmlConfigReader.Config("NewListingScrapper","DEV")
    strUserName = cfg.getConfigValue("UserName")
    strPwd = cfg.getConfigValue("Password")
    #strUrl = str(cfg.getConfigValue("EntryUrl"))

    executable_path = r'C:\Python35\selenium\webdriver\firefox\x86\geckodriver.exe'
    binary = FirefoxBinary('C:/Program Files (x86)/Mozilla Firefox/firefox.exe')
    driver = webdriver.Firefox(executable_path=executable_path)
    #driver = webdriver.Firefox(firefox_binary=binary)
    print(cfg.getConfigValue("EntryUrl"))
    driver.get(cfg.getConfigValue("EntryUrl"))  # load the web page

    #look for user name log in:

    elemUsr = driver.find_element_by_id("member_email")
    elemUsr.send_keys(strUserName)
    elemPwd = driver.find_element_by_id("member_pass")
    elemPwd.send_keys(strPwd)
    elemPwd.send_keys(Keys.RETURN)

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.LINK_TEXT, "Enter Matrix MLS")))
    #now will click Matrix MLS
    window_before = driver.window_handles[0]
    xpath = "/html[@class='wf-effra-n4-active wf-effra-n7-active wf-effra-n3-active wf-effra-n5-active wf-effra-n9-active wf-active']/body/div[@class='content overlay']/div[@class='container']/div[@class='rightPane']/div[@class='box_simple gray agentbox newhar']/div[@class='box_content grid_view']/a[1]"
    elemNextLnk = driver.find_element_by_xpath(xpath)
    elemNextLnk.click()
    #switch to the new window, and click on "new listing"
    time.sleep(10)
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    strPartialText = "New Listing ("
    elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, strPartialText)))
    #get full link text to know the number of properties
    strNextLnkText = elemNextLnk.text
    nRecCnt = int( strNextLnkText[13:].strip(')') )
    #elemNextLnk = driver.find_element_by_partial_link_text(strPartialText)
    elemNextLnk.click()
    time.sleep(3)
    #now the new listing page is being loaded
    pageSizeDdl_id = "m_DisplayCore_dpy2" #the Next link
    elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, pageSizeDdl_id)))
    #now click the first listing in the list
    xpathFirstMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/table[@class='displayGrid nonresponsive ajax_display d58m_show']/tbody/tr[@id='wrapperTable'][1]/td[@class='d58m6']/span[@class='d58m1']/a"
    elemFirstMLS = driver.find_element_by_xpath(xpathFirstMLS)
    sMLS = elemFirstMLS.text
    elemFirstMLS.click()

    #wait for the details page to load
    #xPathMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/div[@class='multiLineDisplay ajax_display d3m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d3m1']/span[@class='display']/table[@class='d3m2']/tbody/tr[2]/td[@class='d3m3']/span[@class='formula']/div[@class='multiLineDisplay ajax_display d48m_show nonresponsive']/table[@id='wrapperTable']/tbody/tr/td[@class='d48m1']/span[@class='display']/table[@class='d48m2']/tbody/tr[3]/td[@class='d48m5']/table[@class='d48m7']/tbody/tr[@class='d48m8']/td[@class='d48m16']/table[@class='d48m17']/tbody/tr[3]/td[@class='d48m19']/span[@class='wrapped-field']"
    xPathNext = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerLeft hideOnMap hideOnSearch hideNoResults']/span[@id='m_lblPagingSummary']/span[@class='pagingLinks']/a[@id='m_DisplayCore_dpy3']"
    NextLinkId = 'm_DisplayCore_dpy3'
    nExceptionCount = 0
    lstScrapResults = []
    nTotalCount = 0
    db = DBMSAccess.MSAccess(r"c:\temp\NewListings.accdb")
    while nTotalCount < nRecCnt-1:
        try:
            rslt = None
            elemNextLnk = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, NextLinkId)))
            pageSource = driver.page_source
            #lstScrapResults.append(PropScrap.parsePropertyDetails(pageSource))
            rslt = PropScrap.parsePropertyDetails(pageSource)
            db.InsertDictionary("NewListings", rslt)
            db.Committ()
            elemNextLnk.click()
            time.sleep(1)
            nTotalCount += 1
            strFailedAttempts = ""
        except Exception as e:
            traceback.print_exc()
            print ('the next link is not found, it will try again')
            strFailedAttempts += "1"
            if len(strFailedAttempts) == 5:
                #if consecutive failed attempts reaches 5, will use an alternative method
                nLvl2TryCount = 0
                try:
                    elemNextLnk = WebDriverWait(driver, 5).until(EC.presence_of_element_located(By.LINK_TEXT, "Next"))
                    pageSource = driver.page_source
                    rslt = PropScrap.parsePropertyDetails(pageSource)
                    db.InsertDictionary("NewListings", rslt)
                    db.Committ()
                    elemNextLnk.click()
                except:
                    print("second level 2 error trapping failed, will try a few more times")
                    nLvl2TryCount +=1
                    if nLvl2TryCount == 5:
                        sys.exit()
            time.sleep(2)

    #now will write the results to database
    writeToCSV(lstScrapResults)


