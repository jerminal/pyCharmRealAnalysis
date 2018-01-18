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
import time
from datetime import date
from datetime import datetime, timedelta
import traceback
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import json

class MatrixScrapper:
    '''
    initializer, gets user name, password, entry url, gecko driver detains, etc.
    '''

    def __init__(self, strConfigFilePath, strConfigSect):
        self._cfg = XmlConfigReader.Config(strConfigFilePath, strConfigSect)
        strUserName = self._cfg.getConfigValue("HARUserName")
        strPwd = self._cfg.getConfigValue("HARPassword")
        strEntryUrl = self._cfg.getConfigValue("EntryUrl")
        executable_path = self._cfg.getConfigValue("GeckoPath")

        binary = FirefoxBinary(self._cfg.getConfigValue("FireFoxBinary"))
        self._driver = webdriver.Firefox(executable_path=executable_path)
        # driver = webdriver.Firefox(firefox_binary=binary)
        print(self._cfg.getConfigValue("EntryUrl"))
        self._driver.get(self._cfg.getConfigValue("StartingUrl"))  # load the web page

        # look for user name log in:
        elemUsr = self._driver.find_element_by_id("member_email")
        elemUsr.send_keys(strUserName)
        elemPwd = self._driver.find_element_by_id("member_pass")
        elemPwd.send_keys(strPwd)
        elemPwd.send_keys(Keys.RETURN)

        (elemNextLnk, nFailureCnt) = self.find_wait_get_element("link_text", "Enter Matrix MLS")
        window_before = self._driver.window_handles[0]
        xpath = "/html[@class='wf-effra-n4-active wf-effra-n7-active wf-effra-n3-active wf-effra-n5-active wf-effra-n9-active wf-active']/body/div[@class='content overlay']/div[@class='container']/div[@class='rightPane']/div[@class='box_simple gray agentbox newhar']/div[@class='box_content grid_view']/a[1]"
        (elemNextLnk, nFailureCnt) = self.find_wait_get_element("xpath", xpath, True)
        time.sleep(3)

        self.wait_for_new_window(self._driver)
        window_after = self._driver.window_handles[1]
        self._driver.close()
        self._driver.switch_to.window(window_after)

        return

    '''
    this procedure waits until new window opens
    '''

    def select_dropdown(self, dropdown_id, option_value):
        dd = self._driver.find_element_by_id(dropdown_id)
        xpath = ".//option[@value='{}']".format(option_value)
        elem= dd.find_element_by_xpath(xpath)
        elem.click()


    def wait_for_new_window(self, timeout=10):
        handles_before = self._driver.window_handles
        yield
        WebDriverWait(self._driver, timeout).until(
            lambda driver: len(handles_before) != len(driver.window_handles))

    '''
    find, wait and get element, if not successful, it will keep on trying for 10 times before quit the program
    '''
    def find_wait_get_element(self, elementType, val, bClick=False):
        nFailureCount = 0
        while nFailureCount < 5:
            try:
                if elementType == "link_text":
                    elem = elemNextLnk = WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located((By.LINK_TEXT, val)))
                elif elementType == "xpath":
                    elem = elemNextLnk = WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, val)))
                elif elementType == "id":
                    elem = elemNextLnk = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.ID, val)))
                elif elementType == "partial_link_text":
                    elem = elemNextLnk = WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, val)))
                elif elementType == "name":
                    elem = elemNextLnk = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.NAME, val)))
                else:
                    elem = elemNextLnk = WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, val)))
                if bClick:
                    elem.click()
                return (elem, nFailureCount)
            except:
                nFailureCount += 1
                self._driver.refresh()
        return (None, nFailureCount)

    '''
    queries the all property search classic page, and get the list of resulting MLSs
    lstParams is a list of tuples of: (xPathToElement, element type, value to be set to element)
    '''
    def QueryAllPropSearchClassicPage(self, lstParams):
        #losad the page first
        lnkAllPropSearch = 'http://matrix.harmls.com/Matrix/Search/AllProperties/Classic'
        self._driver.get(lnkAllPropSearch)
        time.sleep(3)

        #now start looking for the web parts in lstParams, and set values
        for item in lstParams:
            xPath = item[0]
            controlType = item[1]
            val = item[2]
            strDesc = item[3]
            try:
                elem = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, xPath)))
                if controlType == 'TextBox':
                    elem.clear()
                    elem.send_keys(val)
                elif controlType == 'ListItem':
                    if elem.is_selected():
                        if val == False:
                            elem.click()
                    else:
                        if val == True:
                            elem.click()
                elif controlType == 'CheckBox':
                    if elem.is_selected():
                        if val == False:
                            #uncheck the control
                            elem.click()
                    else:
                        if val == True:
                            elem.click()
                else:
                    # error, return False
                    print("Error, control type:{0} with value {1} is not defined!".format(controlType, val))
                    return -1
            except:
                print("Error: Cannot find the element{0}".format(strDesc))
                #return -1
        #now will get the return values
        time.sleep(1)
        xpResultCountLnk = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='ctl12']/table[@class='buttonBar']/tbody/tr/td[@id='m_ucSearchButtons_m_tdACount']/a[@id='m_ucSearchButtons_m_lbLiveCount']/span/span[@id='m_ucSearchButtons_m_clblCount']"
        elemResultCnt = self._driver.find_element_by_xpath(xpResultCountLnk)
        try:
            lstRslt = elemResultCnt.text.split(' ')
            print("Raw result is {0}".format(lstRslt[0]))

            nResultCnt = int(lstRslt[0])
        except:
            nResultCnt = 9999
        print ("Total result count: {0}".format(nResultCnt))
        xpResultLnk = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='ctl12']/table[@class='buttonBar']/tbody/tr/td[@class='link important barleft'][2]/a[@id='m_ucSearchButtons_m_lbSearch']/span[@class='linkIcon icon_default']"
        elemResultLnk = self._driver.find_element_by_xpath(xpResultLnk)
        elemResultLnk.click()

        return nResultCnt

    '''
    scraps the property search result page, and get the mls list
    nRecCnt is hte count of records it supposed to return
    '''
    def ScrapSearchResultPage_New(self, nRecCnt):
        xPathTable = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/table[@class='displayGrid nonresponsive ajax_display d1m_show']"
        xPathNext = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@id='m_upDisplayButtons']/div[1]/div[@id='m_pnlDisplayButtons']/div[@class='resultsMenu tabbedMenu']/div[@class='paging hideOnMap']/span[@id='m_upPaging']/span[@class='pagingLinks']/a[{0}]".format(int(nRecCnt/100)+2)
        hrefPartialNext = "javascript:__doPostBack('m_DisplayCore','Redisplay|"
        tagNextText = "Next"
        lstMLS=[]
        for rep in range(int(nRecCnt/100)+1):
            print("Working on page {0} of {1} records..".format(int(nRecCnt/100), nRecCnt))
            try:
                #find the element containing the mls results table
                elem = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, xPathTable)))
            except:
                print("Error getting Table element containing search results")
                print( traceback.print_exc() )
                return []
            sHtml = elem.get_attribute('innerHTML')
            soup = BeautifulSoup(sHtml, 'lxml')
            strTrigger = "javascript:__doPostBack('m_DisplayCore','Redisplay"
            mlsSearchResults = soup.find_all("a", href=lambda href: href and strTrigger in href)
            for item in mlsSearchResults:
                if item.text.isdigit():
                    nMLS = int(item.text)
                    print("MLS: {0} found".format(nMLS))
                    if nMLS/1000>1:
                        lstMLS.append(nMLS)
            if rep <int(nRecCnt/100):
                nextLinks = self._driver.find_elements_by_link_text("Next")
                for link in nextLinks:
                    strHref = link.get_attribute("href")
                    if hrefPartialNext in strHref:
                        link.click()
                        time.sleep(1)
                        break
                #elemNext = WebDriverWait(self._driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, xPathNext)))
                #elemNext[0].click()
        print("{0} MLSes scrapped".format(len(lstMLS)))
        return lstMLS



    '''
    scraps the property search result page, and get the mls list
    nRecCnt is hte count of records it supposed to return
    '''
    def ScrapSearchResultPage_obselete(self, nRecCnt):
        try:
            xpResultsPerPage = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerRight hideOnSearch hideOnMap'][1]/div/span[@id='m_ucDisplayPicker_m_spnPageSize']/select[@id='m_ucDisplayPicker_m_ddlPageSize']"
            elem = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, xpResultsPerPage)))
            idResultsPerPage = "m_ucDisplayPicker_m_ddlPageSize"
            #self.select_dropdown(idResultsPerPage, "100")

            #elem = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, xpResultsPerPage)))
            #elem.click()
            #elem = Select(elem)

            #elem.select_by_visible_text('100')
            #xpDisplayFormat = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSubHeader']/div[@id='m_pnlSubHeader']/div/table/tbody/tr/td[@class='css_innerRight hideOnSearch hideOnMap'][1]/div/select[@id='m_ucDisplayPicker_m_ddlDisplayFormats']"
            idDisplayFormat = "m_ucDisplayPicker_m_ddlDisplayFormats"
            self.select_dropdown(idDisplayFormat, "1")
            #elem = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, xpDisplayFormat)))
            #elem.select_by_visible_text('Agent Single Line')

        except:
            print("Error getting the Dropdown element")
            print( traceback.print_exc() )
            return []
        try:
            #now wait for the page to reload and check the existence of "next" tag
            xpNext = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@id='m_upDisplayButtons']/div[1]/div[@id='m_pnlDisplayButtons']/div[@class='resultsMenu tabbedMenu']/div[@class='paging hideOnMap']/span[@id='m_upPaging']/span[@class='pagingLinks']/a[5]"
            lstMLS = []
            #now start to scrap the msl numbers
            xpMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/table[@class='displayGrid nonresponsive ajax_display d1m_show']/tbody/tr[@id='wrapperTable'][{0}]/td[@class='d1m5']/span[@class='d1m1']/a"
            #textHref = "javascript:__doPostBack(&#39;m_DisplayCore&#39;,&#39;Redisplay|3,,{0}&#39;)"
            for p in range(0, int(nRecCnt/100) +1):
                #first wait for next element to show up
                elemNext = WebDriverWait(self._driver, 5).until(EC.presence_of_element_located((By.XPATH, xpNext)))
                for x in range(0,99):
                    try:
                        elem = self._driver.find_element_by_xpath(xpMLS.format(x+1))
                        #elem = self._driver.find_element_by_link_text(textHref.format(x))
                        lstMLS.append(elem.text)
                    except:
                        traceback.print_exc()
                        continue
                if p < int(nRecCnt/100):
                    #need to find the next link and click it
                    elemNext.click()
            return lstMLS
        except:
            return []
    '''
        scrapes a a property page and returns a dictionary containing the property details data
    '''

    def wait_for_new_window(self, timeout=10):
        handles_before = self._driver.window_handles
        for x in range(10):
            if len(handles_before) != len(self._driver.window_handles):
                return
            else:
                time.sleep(1)
        '''
        yield
        WebDriverWait(self._driver, timeout).until(
            lambda self._driver: len(handles_before) != len(self._driver.window_handles))
        '''
    def ScrapPropDetailsPage(self, strMLS):
        print('Now scrapping details of MLS#: {0}'.format(strMLS))
        dict = {}
        lstFormInputs = []
        xpMLS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/input[@id='Fm1_Ctrl12_TextBox']"
        lstFormInputs.append((xpMLS, 'TextBox', strMLS, 'MLS entry'))
        nFoundCount = o.QueryAllPropSearchClassicPage(lstFormInputs)
        #here nFoundCount should = 1
        #now click on the only result
        #first look for link with text = mls number, then click on the link
        #elemMLS = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, )))
        #search for the link with the MLS number

        elem=WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, strMLS)))
        elem.click()

        #scrap the details
        #xpMLS = "/html[@class='gr__matrix_harmls_com']/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[3]/div[@id='m_upDisplay']/div[@id='m_pnlDisplayTab']/div[@id='m_divContent']/div[@id='m_pnlDisplay']/div[@class='multiLineDisplay ajax_display d97m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d97m1']/table[@class='d97m2']/tbody/tr[2]/td[@class='d97m4']/span[@class='formula field d97m6']/div[2]/div[@class='multiLineDisplay ajax_display d3m_show nonresponsive']/table/tbody/tr/td/table[@id='wrapperTable']/tbody/tr/td[@class='d3m1']/span[@class='display']/table[@class='d3m2']/tbody/tr[2]/td[@class='d3m3']/span[@class='formula']/div[@class='multiLineDisplay ajax_display d48m_show nonresponsive']/table[@id='wrapperTable']/tbody/tr/td[@class='d48m1']/span[@class='display']/table[@class='d48m2']/tbody/tr[3]/td[@class='d48m5']/table[@class='d48m7']/tbody/tr[@class='d48m8']/td[@class='d48m16']/table[@class='d48m17']/tbody/tr[3]/td[@class='d48m19']/span[@class='wrapped-field']"
        xpMLS = '//span[contains(text(), {0})]'.format(strMLS)
        elemMLS = WebDriverWait(self._driver, 30).until(EC.presence_of_element_located((By.XPATH, xpMLS)))
        sHtml = self._driver.page_source
        dict = self.parsePropertyDetails(sHtml)
        #now scrap lat/lon
        mainWindow = self._driver.window_handles[0]
        xpMap = '//*[@title="View Map"]'
        elemViewMap = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, xpMap)))
        if not elemViewMap is None:
            elemViewMap.click()
            # switch to the map view window
            self.wait_for_new_window()
            mapWindow = self._driver.window_handles[1]
            self._driver.switch_to.window(mapWindow)
            # look for the tag with id: m_ucStreetViewService_m_hfParams
            tagId = "m_ucStreetViewService_m_hfParams"
            # elemLatLon = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, tagId)))
            elemLatLon = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.ID, tagId)))
            # strip lat/lon:
            tagText = str(elemLatLon.get_attribute("value"))
            (lat, lon) = tagText.split("$")[1:3]
            self._driver.close()
            self._driver.switch_to.window(mainWindow)

        else:
            (lat, lon) = (None, None)
        dict["geoLat"] = lat
        dict["geoLon"] = lon
        print ("scrapping MLS#:{0} done.".format(strMLS))
        return dict

    def parsePropertyDetails(self, sHtml):
        soup = BeautifulSoup(sHtml, 'lxml')
        # extract section 1 details- basic property info
        dataCollect = []
        table = soup.find_all("table", {"class": "d48m17"})
        for tr in table[0].findAll("tr"):
            for td in tr.findAll("td"):
                dataCollect.append(td.find(text=True))
        # extract section 2 details - listing agent information

        tables = soup.find_all("table", {"class": "d48m7"})
        for table in tables:
            for tr in table.findAll("tr"):
                for td in tr.findAll("td"):
                    dataCollect.append(td.find(text=True))
        print(dataCollect)
        dictColumns = {"MLSNum": "ML#: ", "Status": "Status: ", "ListPrice": "List Price: ", "Address": "Address: ",
                       "Area": "Area: ", "LPperSqft": "LP/SF: ", "TaxID": "Tax Acc #: ", "DaysOnMarket": "DOM: ",
                       "City": "City: ", "State": "State: ", "County": "County: ", "MasterPlanned": "Master Planned: ",
                       "Location": "Location:", "MarketArea": "Market Area:", "Subdivision": "Subdivision: ",
                       "SectionNum": "Secction #:", "LotSize": "Lot Size: ", "BldgSqft": "SqFt: ",
                       "LotValue": "Lot Value:", "LeaseAlso": "Lease Also:", "YearBuilt": "Year Built: ",
                       "LegalDesc": "Legal Desc: ",
                       "ListBroker": "List Broker: ", "ListAgent": "List Agent: ", "BrokerAddress": "Address: ",
                       "LicensedSupervisor": "Licensed Supervisor:", "SchoolDistrict": "School District: ",
                       "ElemSchool": "Elem: ",
                       "MiddleSchool": "Middle: ", "HighSchool": "High: ", "Style": "Style: ", "Stories": "# Stories: ",
                       "Type": "Type: ", "Access": "Access: ", "Acres": "Acres: ", "Bedrooms": "Bedrooms: ",
                       "Baths": "Baths F/H: ",
                       "Builder": "Builder Nm: ", "Oven": "Oven:", "Roof": "Roof: ", "Flooring": "Flooring: ",
                       "Foundation": "Foundation: ", "Countertops": "Countertops: ", "PrvtPool": "Prvt Pool:",
                       "WaterfrontFeat": "Waterfront Feat: ", "ListDate": "List Date: ", "MaintFee": "Maint. Fee: ",
                       "TaxRate": "Tax Rate: ", "Zip": "Zip Code: ", "AgentEmail": "Agent Email:",
                       "AgentPhone": "Agent Phone: ",
                       "Connections": "Connect: ", "Interior": "Interior: ", "MasterBath": "Master Bath:",
                       "ExteriorCons": "Exterior Constr: ", "Range": "Range:", "LotDesc": "Lot Description: ",
                       "Heating": "Heat: ",
                       "Cooling": "Cool: ", "BedroomsDesc": "Bedrooms: ", "ListAgentId": "ListAgentId: ",
                       "ListAgentName": "ListAgentName:", "ListBrokerId": "ListBrokderId:",
                       "ListBrokerName": "ListBrokerName:",
                       "SellAgentTRECId": "TREC #: ", "SalePrice": "Sale Price: ", "CloseDate": "Close Date: ",
                       "SalePricePerSqft": "SP$/SF: ", "DaysToClose": "Days to Close: ", "FinTerms": "Terms:",
                       "AmortizeYears": "Amortize Years: ",
                       "NewLoan": "New Loan: ", "PendingDate": "Pending Date: ", "EstCloseDate": "Est Close Dt: ",
                       "CoOp": "CoOp: "
                       }
        dictResults = {}
        for key in dictColumns:
            try:
                idx = dataCollect.index(dictColumns[key])
                dictResults[key] = dataCollect[idx + 1]
            except:
                print("{0} not found".format(dictColumns[key]))
        print(dictResults)
        # now do some clean up
        # BldgSqft: example: 2,705 / Appr Dist, needs to get rid of the part after /
        try:
            entry = dictResults["BldgSqft"]
            dictResults["BldgSqft"] = int((entry.split(' ')[0]).replace(',', ''))
        except:
            print("Exception occured while trying to parse BldgSqft. Original value: {0}".format(entry))
            dictResults["BldgSqft"] = None

        # Days on market: sometimes there is an asterisk after the number

        try:
            entry = dictResults['DaysOnMarket']
            if entry[-1:] == '*':
                dictResults['DaysOnMarket'] = entry[:-1]
        except:
            print("Exception occured while trying to parse DOM. Original value: {0}".format(entry))
            dictResults["DaysOnMarket"] = None
        # lot size:
        try:
            entry = dictResults["LotSize"]
            dictResults["LotSize"] = int((entry.split(' ')[0]).replace(',', ''))
        except:
            print("Exception occured while trying to parse Lotsize. Original value: {0}".format(entry))
            dictResults["LotSize"] = None
        # LPperSqft
        try:
            entry = dictResults['LPperSqft'][1:]  # pick the number part, leave out the dollar sign
            dictResults['LPperSqft'] = float(entry.replace(',', ''))
        except:
            print("Exception occured while trying to parse LPperSqft. Original value: {0}".format(entry))
            dictResults["LPperSqft"] = None
        # ListPrice
        try:
            entry = dictResults['ListPrice'][1:]  # pick the number part, leave out the dollar sign
            dictResults['ListPrice'] = float(entry.replace(',', ''))
        except:
            print("Exception occured while trying to parse ListPrice. Original value: {0}".format(entry))
            dictResults["ListPrice"] = None
        # YearBuilt
        try:
            entry = dictResults['YearBuilt']
            dictResults['YearBuilt'] = int(entry.split(' ')[0])
        except:
            print("Exception occured while trying to parse YearBuilt. Original value: {0}".format(entry))
            dictResults["YearBuilt"] = None
        # now separate list agent id and name
        try:
            entry = dictResults['ListAgent']
            dictResults['ListAgentId'] = entry.split('/')[0]
            dictResults['ListAgentName'] = entry.split('/')[1]
        except:
            print("Error occured while trying to generate agent id and name. original value: {0}".format(entry))
            dictResults['ListAgentId'] = entry
            dictResults['ListAgentName'] = entry
        # now separate broker id and name
        try:
            entry = dictResults['ListBroker']
            dictResults['ListBrokerId'] = entry.split('/')[0]
            dictResults['ListBrokerName'] = entry.split('/')[1]
        except:
            print("Error occured while trying to generate broker id and name. original value: {0}".format(entry))
            dictResults['ListBrokerId'] = entry
            dictResults['ListBrokerName'] = entry
        return dictResults

    def scrapNewProperty(self, datStart, datEnd, strPropType):
        return

    def scrapSoldProperty(self, datStart, datEnd, strPropType):
        return

if __name__ == "__main__":
    o = MatrixScrapper("AllPropScrapper", "DEV")
    lstFormInputs = []
    datFrom = date.today() + timedelta(days=-3)
    datTo = date.today()
    # now check/uncheck the property status boxes, and set start/end date values
    xpChkActive = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[2]/td[1]/div/input[@class='checkbox']"
    xpChkOP = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[3]/td[1]/div/input[@class='checkbox']"
    xpChkPCS = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[4]/td[1]/div/input[@class='checkbox']"
    xpChkPending = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[5]/td[1]/div/input[@class='checkbox']"
    xpChkSold = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[6]/td[1]/div/input[@class='checkbox']"
    xpInputActive = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[2]/td[2]/input[@id='FmFm1_Ctrl16_20915_Ctrl16_TB']"
    xpInputSold = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[2]/table[@class='S_MultiStatus']/tbody/tr[6]/td[2]/input[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']"

    # now select the property type
    xpPropTypeRes = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[1]"
    xpPropTypeCnd = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[2]"
    xpPropTypeLnd = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[3]"
    xpPropTypeRnt = "/html/body/form[@id='Form1']/div[@class='stickywrapper']/div[@class='tier3']/table/tbody/tr/td/div[@class='css_container']/div[@id='m_upSearch']/div[@id='m_pnlSearchTab']/div[@id='m_pnlSearch']/div[@class='css_content']/div[@id='m_sfcSearch']/div[@class='searchForm']/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]/select[@id='Fm1_Ctrl129_LB']/option[5]"

    strDtRange = datFrom.strftime("%m/%d/%Y") + '-' + datTo.strftime("%m/%d/%Y")

    lstFormInputs.append((xpChkActive, 'CheckBox', True, 'Active check box'))
    lstFormInputs.append((xpChkOP, 'CheckBox', False, 'Option pending check box'))
    lstFormInputs.append((xpChkPCS, 'CheckBox', False, 'Pending cont to show check box'))
    lstFormInputs.append((xpChkPending, 'CheckBox', False, 'pending check box'))
    #lstFormInputs.append((xpChkSold, 'CheckBox', False, 'sold check box'))
    lstFormInputs.append((xpInputActive, 'TextBox', strDtRange, 'active text box'))
    lstFormInputs.append((xpChkSold, 'TextBox', '', 'sold check box'))
    lstFormInputs.append((xpPropTypeRes, 'ListItem', True, 'residential list item'))
    lstFormInputs.append((xpPropTypeCnd, 'ListItem', False, 'condo list item'))
    lstFormInputs.append((xpPropTypeLnd, 'ListItem', False, 'land list item'))
    lstFormInputs.append((xpPropTypeRnt, 'ListItem', False, 'rent list item'))

    nFoundCount = o.QueryAllPropSearchClassicPage(lstFormInputs)
    if nFoundCount > 5000:
        print("more than 5000 results returned. quit....")
    else:
        lstMLS = o.ScrapSearchResultPage_New(nFoundCount)
        #now go back to the AllPropSearchClassicPage and search for MLS only
        xpMLS = ""
        lstResults = []
        for mls in lstMLS:
            lstResults.append(o.ScrapPropDetailsPage(str(mls)))

        with open("result.json", 'w') as fp:
            json.dump(lstMLS, fp)