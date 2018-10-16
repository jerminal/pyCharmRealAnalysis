import XmlConfigReader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import re
import traceback
from datetime import date
import json
import glob

class cMatrixScrapper:
    def __init__(self, strConfigFilePath, strConfigSect ):
        #initialize the object, and connect to har
        print("Initialize Matrix scrapper")
        self._cfg = XmlConfigReader.Config(strConfigFilePath, strConfigSect)
        executable_path = self._cfg.getConfigValue("GeckoPath")
        strBrowser = self._cfg.getConfigValue("Browser")
        print("Opening {0} browser".format(strBrowser))

        if strBrowser == "Chrome":
            self._driver = webdriver.Chrome()
        #self.SignIntoMatrix()
        return

    def __del__(self):
        print("Destroyong Matrix scrapper")
        self._driver.quit()

    def SignIntoMatrix(self):
        # driver = webdriver.Firefox(firefox_binary=binary)
        print("Signing into {0}".format(self._cfg.getConfigValue("EntryUrl")))
        self._driver.get(self._cfg.getConfigValue("StartingUrl"))  # load the web page
        strUserName = self._cfg.getConfigValue("HARUserName")
        strPwd = self._cfg.getConfigValue("HARPassword")
        strEntryUrl = self._cfg.getConfigValue("EntryUrl")

        # look for user name log in:
        elemUsr = self._driver.find_element_by_id("member_email")
        elemUsr.send_keys(strUserName)
        elemPwd = self._driver.find_element_by_id("member_pass")
        elemPwd.send_keys(strPwd)
        elemPwd.send_keys(Keys.RETURN)

        window_before = self._driver.window_handles[0]
        elemNextLnk  = self.find_wait_get_element("link_text", "Enter Matrix MLS", True)

        #xpath = "/html[@class='wf-effra-n4-active wf-effra-n7-active wf-effra-n3-active wf-effra-n5-active wf-effra-n9-active wf-active']/body/div[@class='content overlay']/div[@class='container']/div[@class='rightPane']/div[@class='box_simple gray agentbox newhar']/div[@class='box_content grid_view']/a[1]"
        #elemNextLnk = self.find_wait_get_element("xpath", xpath, True)
        #time.sleep(3)

        self.wait_for_new_window(self._driver)
        window_after = self._driver.window_handles[1]
        self._driver.close()
        self._driver.switch_to.window(window_after)
        print("signed in")
        return True

    '''
    Input parameters:
    desc: a general description of what the tag is/does
    tag: tag: a, input, select, etc.
    type: tag type: input, checkbox, option, etc.
    xp: xpath to the tag on the webpage
    val: tag value, it can be True/False, string, etc.
    
    '''
    def set_tag_value(self, desc, tag, type, xp, val):
        try:
            elem = self._driver.find_element_by_xpath(xp)
        except:
            print ('Error! Tag Not found!  xpath: {0}'.format(xp))
            return False

        if tag == 'input':
            if type == 'text':
                elem.clear()
                elem.send_keys(val)
                return True
            elif type == 'checkbox':
                if elem.is_selected() != val:
                    elem.click()
                return True
            else:
                print('Unknown tag type enountered for tag: {0}. Tag type: {1} is unknown.'.format(tag, type))
                return False
        elif tag == 'select':
            if type.split('-')[0] == 'option':
                if len(val) > 0:
                    for option in elem.find_elements_by_tag_name('option'):
                        if type.split('-')[1] == 'text':
                            if option.text == val:
                                option.click()
                                return True
                        elif type.split('-')[1] == 'value':
                            if option.get_attribute('value') == val:
                                option.click()
                                return True
                        elif type.split('-')[1] == 'title':
                            if option.get_attribute('title') == val:
                                option.click()
                                return True
                        else:
                            print('Unkown option select criteria')
                            return False
            else:
                print('Unkown tag type encountered for tag {0}. Tag type: {1} is unknown.'.format(tag, type))
                return False
        else:
            print('Unknown tag encountered: Tag {0} is unknown.'.format(tag))
            return False

    def click_element(self, xpath):
        try:
            elem = elemNextLnk = WebDriverWait(self._driver, 30).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
        except:
            print('Web element not found! Element xpath: {0}'.format(xpath))
            return False
        try:
            elem.click()
            return True
        except:
            print('Web element not clickable! Element xpath: {0}'.format(xpath))
            return False

    def wait_for_new_window(self, timeout=10):
        handles_before = self._driver.window_handles
        yield
        WebDriverWait(self._driver, timeout).until(
            lambda driver: len(handles_before) != len(driver.window_handles))

    '''
    find, wait and get element, if not successful, it will keep on trying for 10 times before quit the program
    '''
    def find_wait_get_element(self,elementType, val, bClick=False, waitSeconds = 10):
        try:
            if elementType == "link_text":
                elem = elemNextLnk = WebDriverWait(self._driver, waitSeconds).until(
                    EC.presence_of_element_located((By.LINK_TEXT, val)))
            elif elementType == "xpath":
                elem = elemNextLnk = WebDriverWait(self._driver, waitSeconds).until(
                    EC.presence_of_element_located((By.XPATH, val)))
            elif elementType == "id":
                elem = elemNextLnk = WebDriverWait(self._driver, waitSeconds).until(EC.presence_of_element_located((By.ID, val)))
            elif elementType == "partial_link_text":
                elem = elemNextLnk = WebDriverWait(self._driver, waitSeconds).until(
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, val)))
            elif elementType == "name":
                elem = elemNextLnk = WebDriverWait(self._driver, waitSeconds).until(EC.presence_of_element_located((By.NAME, val)))
            else:
                elem = elemNextLnk = WebDriverWait(self._driver, waitSeconds).until(
                    EC.presence_of_element_located((By.TAG_NAME, val)))
            if bClick:
                elem.click()
            return elem
        except:
            raise Exception('Error! Cannot find element. Type: {0}, value: {1}'.format(elementType, val))


    '''
    Run the search results page, it goes through the MLS in the list one by one, 
    compare against the scrapped list, it will scrap the details if it finds a mls link that's not in the list
    nResultCount: The number of search results
    '''
    def depricated_RunSearchResultsPage(self, nResultCount, strPropType):
        jsonPath = self._cfg.getConfigValue("JsonPath")
        lstMLS = [s.lstrip(jsonPath + "\\").rstrip(".json") for s in glob.glob("{0}\\*.json".format(jsonPath))]
        xpMLSs = ".//td[@class='d1m5']/span[@class='d1m1']" #this is the elements containing mls results

        while True:
            elemMLSs = self._driver.find_elements_by_xpath(xpMLSs)
            xpTester = ".//div[@class='tabSelected']"
            for elemMLS in elemMLSs:
                elemChild = elemMLS.find_element_by_xpath(".//a[starts-with(@href,'javascript:__doPostBack')]")
                if elemChild.text not in lstMLS:
                    #if the mls is not in the list of already scrapped MLS, scrap the details:
                    elemMLS.click()
                    elemChild.click()
                    #switch window handle and scrap results
                    #get the result, if result is unsuccessful, log it and try again
                    nCount = self.ScrapResultPageDetails(strPropType)
                    self._driver.navigate().back()

            #when it's through, check if there is an active "Next" element
            # look for the "next" tag to click
            xpNextOrPrev = ".//a[contains(@href, 'javascript:__doPostBack('m_DisplayCore','Redisplay|,,']"
            elems = self._driver.find_elements_by_xpath(xpNextOrPrev)
            bNextElementClickable = False
            for elem in elems:
                if elem.text == 'Next':
                    # click the next link
                    bNextElementClickable = True
                    elem.click()
                    time.sleep(2)
            if bNextElementClickable == False:
                #there is no clickable next alement anymore, break out
                break

            '''
                 sccrape all property page based on input
                 oStatus: [(text, value(true, false),date_range_as_string)]; example('Active', False, '7/31/2003-9/1/2003')
                lstPropType: ['Single-Family', 'Townhouse/Condo','Lots','Multi-Family','Rental']
                ZipCode:

            '''

    def ProcessAllPropClassicSearchResultsPage(self, nRecCount, bSaveCSV = True):
        '''
            On the Results page, if bSaveCSV = true, it will click to download CSV file, otherwise it will switch to single page view
        '''
        # Search for the master check box, and check it
        #"//*[@id="m_pnlDisplay"]/table/thead/tr/th[1]/span/input"
        if bSaveCSV:
            try:
                xpAllLink = "//a[@id='m_lnkCheckAllLink']"
                if not self.click_element(xpAllLink):
                    raise Exception('Error occured while trying to click the Check All link')
                time.sleep(1)
                # Click the export button and save the csv file
                xpExportButton = "//a[@id='m_lbExport']"
                if not self.click_element(xpExportButton):
                    raise Exception('Error occured while trying to click the Export link')
                time.sleep(1)
                #now it will bring up another webpage, we need to click the final export button
                xpFileSave = "//a[@id='m_btnExport']"
                if not self.click_element(xpFileSave):
                    raise Exception('Error occured while trying to click Export button')
                return nRecCount
            except:
                print("exception happened while trying to download csv")
                traceback.print_exc()
                return 0
        else:
            #Search for the first mls link and click it
            xpMLS = '//td[@class="d1m5"]/span[@class="d1m1"]/a'
            #get the first MLS link
            try:
                elemMLS = self._driver.find_elements_by_xpath(xpMLS)[0]
            except:
                print("Error locating the MLS tag. Tag xpath: {0}".format(xpMLS))
                return 0
            if elemMLS.get_attribute('href') is not None:
                elemMLS.click()
                return nRecCount
            else:
                return 0



    def FilterAllPropClassicSearchPage(self, lstCriteria):
        '''
        input parameters:
        lstCriteria: example
            [
            ('MLS#', 'input','text','//input[@id="Fm1_Ctrl12_TextBox"]', '0123456789'),
            ('Active Check', 'input', 'checkbox', '//input[@value="20915" and @name="Fm1_Ctrl16_LB"], False),
            ('ActiveText', 'input', 'text', ".//*[@id='FmFm1_Ctrl16_20915_Ctrl16_TB']", '01/01/2018-03/01/2018'),
            ('Option Pending Check', 'input', 'checkbox', ".//*[@name='Fm1_Ctrl16_LB' and @value='20918']", False),
            ('Option Pending Text', 'input', 'text', ".//*[@id='FmFm1_Ctrl16_20918_Ctrl16_TB']", '01/01/2018-03/01/2018'),
            ('Pend Cont to Show Check', 'input', 'checkbox', ".//*[@name='Fm1_Ctrl16_LB' and @value='20920']", False),
            ('Pend Cont to Show Text', 'input', 'text', ".//*[@id='FmFm1_Ctrl16_20920_Ctrl16_TB']", '01/01/2018-03/01/2018'),
            ('Pending Check', 'input', 'checkbox', ".//*[@name='Fm1_Ctrl16_LB' and @value='20919']", False)
            ('Pending Text', 'input' 'text' ,".//*[@id='FmFm1_Ctrl16_20919_Ctrl16_TB']", '01/01/2018-03/01/2018'),
            ('Sold Check', 'input', 'checkbox', ".//*[@name='Fm1_Ctrl16_LB' and @value='20916']", True),
            ('Sold Text', 'input', 'text', ".//*[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']", '01/01/2018-03/01/2018'),
            ('Withdrawn Check', 'input', 'checkbox', ".//*[@name='Fm1_Ctrl16_LB' and @value='20922']", False),
            ('Widthdrawn Text', 'input', 'text',".//*[@id='FmFm1_Ctrl16_20922_Ctrl16_TB']", '01/01/2018-03/01/2018'),
            ('Single-Family Select', 'select', 'option-text', './/select[@id="Fm1_Ctrl129_LB"]', 'Single-Family'),
            ('Townhouse Select', 'select', 'option-value', './/select[@id="Fm1_Ctrl129_LB"]', '23708'),
            ('Lots Select', 'select', 'option-title', './/select[@id="Fm1_Ctrl129_LB"]', 'Lots'),
            ('Multi-Family Select', 'select', 'option-text', './/select[@id="Fm1_Ctrl129_LB"]', 'Multi-Family'),
            ('Country Homes Select', 'select', 'option-value', './/select[@id="Fm1_Ctrl129_LB"]', '20923'),
            ('Mid/Hi-Rise Select', 'select', 'option-value', './/select[@id="Fm1_Ctrl129_LB"]', '23709'),
            ('Rent Select', 'select', 'option-text', './/select[@id="Fm1_Ctrl129_LB"]', 'Rental'),
            ('ZipCode Text','input','text', './/[@id="Fm1_Ctrl19_TextBox"]', '77007'),
            ]
        return value:
        0: logic failure
        >5000: too many records
        between 1-5000: success
        '''
        # load the page
        strPageLink = "http://matrix.harmls.com/Matrix/Search/AllProperties/Classic"
        self._driver.get(strPageLink)
        # verify the page load completes by checking existance of the first search creteria
        xpResults = './/a[@id="m_ucSearchButtons_m_lbSearch"]'
        elemResults = self.find_wait_get_element('xpath', xpResults, False, 30)
        if elemResults is None:
            return -1
        for criteria in lstCriteria:
            xp = criteria[3]
            val = criteria[4]
            tag = criteria[1]
            type = criteria[2]
            desc = criteria[0]
            if self.set_tag_value(desc, tag, type, xp, val) == False:
                return -1
        time.sleep(3) #pause for 3 seconds for the results to update
        ##get the result link and result count
        xpResultCntLnk = ".//*[@id='m_ucSearchButtons_m_clblCount']"
        elemResultCntLnk = self.find_wait_get_element('xpath', xpResultCntLnk, False,30)
        print(elemResultCntLnk.text)
        nResultCount = int(re.findall(r'\d+', elemResultCntLnk.text)[0])
        return nResultCount

    def QueryPropertyByMLS(self, strMLS, bSaveHtml=True, bFindLatLon=True):
        lstCriteria = [
            ('Active Check', 'input', 'checkbox', '//input[@value="20915" and @name="Fm1_Ctrl16_LB"]', False),
            ('MLS#', 'input', 'text', '//input[@id="Fm1_Ctrl12_TextBox"]', strMLS)
        ]
        nRecCount = self.FilterAllPropClassicSearchPage(lstCriteria)
        if nRecCount ==1:
            xpResultLnk = './/a[@id="m_ucSearchButtons_m_lbSearch"]'
            elemResultCntLnk = self.find_wait_get_element('xpath', xpResultLnk, True, 30)
        return nRecCount

    def DownloadPropHistoryToCSVByZip(self,datFrom, datTo, strZip):
        '''
        :param datFrom: date, from date;
        :param datTo: date, to date
        :param strZip: string zip code
        :return: Record count if success (0,5000), 0 or over 5000 if fail
        '''

        nRecCount = o.QuerySoldAllPropClassicByZip(datFrom, datTo, strZip)
        nReturn = o.ProcessAllPropClassicSearchResultsPage(nRecCount, True)
        return nReturn

    def GetLatLonFromMLSNum(self, strMLS):
        nRecCount = o.QueryPropertyByMLS(strMLS, False, True)
        o.ProcessAllPropClassicSearchResultsPage(nRecCount, False)
        (lat, lon) = o.GetLatLonFromPropDetailPage()
        return (lat, lon)

    def QuerySoldAllPropClassicByZip(self, datFrom, datTo, strZip=None, lstPropType=None):
        '''
        :param datFrom: From Date, Date
        :param datTo: To Date, Date
        :param strZip: Zip code. string. It will skip Zipcode if it's None
        :param lstPropType: list. a list of property types, if will cover all properties if None
        :return:
        '''
        strDateRange = datFrom.strftime('%m/%d/%Y') + '-' + datTo.strftime('%m/%d/%Y')
        lstCriteria = [
            ('Active Check', 'input', 'checkbox', '//input[@value="20915" and @name="Fm1_Ctrl16_LB"]', False),
             ('Sold Check', 'input', 'checkbox', ".//*[@name='Fm1_Ctrl16_LB' and @value='20916']", True),
             ('Sold Text', 'input', 'text', ".//*[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']", strDateRange),
             ]
        if strZip is not None:
            lstCriteria.append((('ZipCode Text', 'input', 'text', './/input[@id="Fm1_Ctrl19_TextBox"]', strZip)))
        if lstPropType is not None:
            for propType in lstPropType:
                if propType == 'Single-Family':
                    lstCriteria.append(('Single-Family Select', 'select', 'option-text', './/select[@id="Fm1_Ctrl129_LB"]', 'Single-Family'))
                elif propType == 'Townhouse':
                    lstCriteria.append(('Townhouse Select', 'select', 'option-value', './/select[@id="Fm1_Ctrl129_LB"]', '23708'))
                elif propType == 'Lots':
                    lstCriteria.append(
                        ('Lots Select', 'select', 'option-title', './/select[@id="Fm1_Ctrl129_LB"]', 'Lots'))
                elif propType == 'Multi-Family':
                    lstCriteria.append(
                        ('Multi-Family Select', 'select', 'option-text', './/select[@id="Fm1_Ctrl129_LB"]',
                         'Multi-Family'))
                elif propType == 'Country home':
                    lstCriteria.append(
                        ('Country Homes Select', 'select', 'option-value', './/select[@id="Fm1_Ctrl129_LB"]', '20923'))
                elif propType == 'Mid/Hi-Rise':
                    lstCriteria.append(
                        ('Mid/Hi-Rise Select', 'select', 'option-value', './/select[@id="Fm1_Ctrl129_LB"]', '23709'))
                elif propType == 'Rental':
                    lstCriteria.append(
                        ('Rent Select', 'select', 'option-text', './/select[@id="Fm1_Ctrl129_LB"]', 'Rental'))
                else:
                    print('Property type not recongnized. Property type: {0}'.format(propType))
        nRecCount = self.FilterAllPropClassicSearchPage(lstCriteria)
        if nRecCount >0 and nRecCount<5000:
            xpResultLnk = './/a[@id="m_ucSearchButtons_m_lbSearch"]'
            elemResultCntLnk = self.find_wait_get_element('xpath', xpResultLnk, True, 30)
        return nRecCount

    def depricate_RunAllPropSearchPage(self, lstStatus, strPropType, strZipCode):
        '''
        return value:
        0: logic failure
        >5000: too many records
        between 1-5000: success
        '''
        # load the page
        strPageLink = "http://matrix.harmls.com/Matrix/Search/AllProperties/Classic"
        self._driver.get(strPageLink)
        # verify the page load completes by checking existance of the first search creteria

        # Load searh criteria, if an element is not found, it returns with False and with a string explanation of the error
        dictStatus = {'Active': (
        ".//*[@name='Fm1_Ctrl16_LB' and @value='20915']", ".//*[@id='FmFm1_Ctrl16_20915_Ctrl16_TB']"),
                      'Option Pending': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='20918']", ".//*[@id='FmFm1_Ctrl16_20918_Ctrl16_TB']"),
                      'Pend Cont to Show': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='20920']", ".//*[@id='FmFm1_Ctrl16_20920_Ctrl16_TB']"),
                      'Pending': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='20919']", ".//*[@id='FmFm1_Ctrl16_20919_Ctrl16_TB']"),
                      'Sold': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='20916']", ".//*[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']"),
                      'Withdrawn': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='20922']", ".//*[@id='FmFm1_Ctrl16_20922_Ctrl16_TB']"),
                      'Expired': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='20917']", ".//*[@id='FmFm1_Ctrl16_20917_Ctrl16_TB']"),
                      'Terminated': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='20921']", ".//*[@id='FmFm1_Ctrl16_20921_Ctrl16_TB']"),
                      'Incomplete': (
                      ".//*[@name='Fm1_Ctrl16_LB' and @value='23706']", ".//*[@id='FmFm1_Ctrl16_23706_Ctrl16_TB']")
                      }
        for oStatus in lstStatus:
            # get the xpaths
            xPaths = dictStatus[oStatus[0]]
            xpChk = xPaths[0]  # get the xpath to the check box
            xpTxt = xPaths[1]  # get the xpath to the textbox
            elemChk = self._driver.find_element_by_xpath(xpChk)
            # now check/uncheck as needed
            if elemChk.is_selected() != oStatus[1]:
                elemChk.click()
            if elemChk.is_selected():  # when it's selected, populate the date range
                elemTxt = self._driver.find_element_by_xpath(xpTxt)
                elemTxt.clear()
                if oStatus[2] is None or len(oStatus[2]) > 0:
                    elemTxt.send_keys(oStatus[2])

        '''the following section selects the property type'''
        xpSelect = ".//*[@id='Fm1_Ctrl129_LB']"  # this is the xpath to find the select element
        elemSelect = self._driver.find_element_by_xpath(xpSelect)
        for option in elemSelect.find_elements_by_tag_name('option'):
            if strPropType == option.text or len(strPropType) == 0:
                option.click()

        '''Now fill in the zip code, if marked'''
        if len(strZipCode)> 0 :
            xPath = ".//*[@id='Fm1_Ctrl19_TextBox']"
            elemZip = self._driver.find_element_by_xpath(xPath)
            elemZip.send_keys(strZipCode)
        time.sleep(2)
        ##get the result link and result count
        xpResultCntLnk = ".//*[@id='m_ucSearchButtons_m_clblCount']"
        xpResultLnk = ".//*[@id='m_ucSearchButtons_m_lbSearch']"
        elemResulCnttLnk = self._driver.find_element_by_xpath(xpResultCntLnk)

        nResultCount = int(re.findall(r'\d+', elemResulCnttLnk.text)[0])
        if nResultCount> 0 and nResultCount < 5000:
            elemResultLnk = self._driver.find_element_by_xpath(xpResultLnk)
            nTryCount = 0
            while True:
                elemResultLnk.click()
                xpMLSHeader = ".//th[@data-mlheader='1\\bMLS #']"
                try:
                    elemMLSHeader = WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpMLSHeader)))
                    break
                except:
                    nTryCount += 1
                    if nTryCount < 10:
                        self._driver.back()
                    else:
                        return -1
            nReturn =  self.DownloadSearchResultsCSV(nResultCount)
            #click the back button to go back to the results list page
            xpBackButton = "//a[@id='m_btnBack']"
            elemBackButton = self._driver.find_element_by_xpath(xpBackButton)
            elemBackButton.click()

            #now save each property details as htmls:
            xpViewList = "//select[@id='m_ucDisplayPicker_m_ddlDisplayFormats']"
            elemViewList = WebDriverWait(self._driver, 30).until(EC.presence_of_element_located((By.XPATH, xpViewList)))
            #elemViewList = self._driver.find_element_by_id('m_ucDisplayPicker_m_ddlDisplayFormats')
            pathHtml = self._cfg.getConfigValue("JsonPath")
            for option in elemViewList.find_elements_by_tag_name('option'):
                if option.text == 'Agent Full':
                    option.click()
                    break
            i = 0
            while True:
                # now save page source for each search results
                xpNextButton = "//a[@id='m_DisplayCore_dpy3']"
                elemNextButton = WebDriverWait(self._driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, xpNextButton)))
                # elemNextButton  = self._driver.find_element_by_xpath(xpNextButton)

                outputFile = open(pathHtml + "\\" + str(i)+".html","w")
                outputFile.write(self._driver.page_source)
                outputFile.close()
                #Now need to get the latlon page
                xpViewMap = "//a[@title='View Map']"
                elemViewMap = self._driver.find_element_by_xpath(xpViewMap)
                if elemViewMap.get_attribute('href') is not None:
                    latlon = self.GetLatLong(elemViewMap)
                    outputFile = open(pathHtml + "\\latlon_" + str(i) + ".json", "w")
                    #outputFile.write(latlon)
                    #outputFile.close()
                    json.dump(latlon, outputFile)
                    outputFile.close()
                i+=1
                time.sleep(1)
                elemNextButton = WebDriverWait(self._driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, xpNextButton)))
                attrHref = elemNextButton.get_attribute('href')
                if attrHref is None:
                    break
                else:
                    elemNextButton.click()

            return nReturn
        else:
            return nResultCount
        '''    
        if nResultCount > 0:

            elemResultLnk = self._driver.find_element_by_xpath(xpResultLnk)
            nTryCount = 0
            while True:
                elemResultLnk.click()
                # time.sleep(2)
                xpMLSHeader = ".//th[@data-mlheader='1\\bMLS #']"
                try:
                    elemMLSHeader = WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpMLSHeader)))
                    break
                except:
                    nTryCount += 1
                    if nTryCount < 10:
                        self._driver.back()
                    else:
                        return False
        #Here will scrap the results list page
        self.RunSearchResultsPage(nResultCount, strPropType)
        '''
        '''
             sccrape all property page based on input
             oStatus: [(text, value(true, false),date_range_as_string)]; example('Active', False, '7/31/2003-9/1/2003')
            lstPropType: ['Single-Family', 'Townhouse/Condo','Lots','Multi-Family','Rental']
            ZipCode:
            
        '''
    def depricated_RunAllPropSearchPage(self, lstStatus, strPropType, ZipCode):
        """

        :rtype: object
        """
        # load the page
        strPageLink = "http://matrix.harmls.com/Matrix/Search/AllProperties/Classic"
        self._driver.get(strPageLink)
        #verify the page load completes by checking existance of the first search creteria

        # Load searh criteria, if an element is not found, it returns with False and with a string explanation of the error
        dictStatus = {'Active':(".//*[@name='Fm1_Ctrl16_LB' and @value='20915']", ".//*[@id='FmFm1_Ctrl16_20915_Ctrl16_TB']"),
                      'Option Pending':(".//*[@name='Fm1_Ctrl16_LB' and @value='20918']",".//*[@id='FmFm1_Ctrl16_20918_Ctrl16_TB']"),
                      'Pend Cont to Show':(".//*[@name='Fm1_Ctrl16_LB' and @value='20920']",".//*[@id='FmFm1_Ctrl16_20920_Ctrl16_TB']"),
                      'Pending':(".//*[@name='Fm1_Ctrl16_LB' and @value='20919']",".//*[@id='FmFm1_Ctrl16_20919_Ctrl16_TB']"),
                      'Sold':(".//*[@name='Fm1_Ctrl16_LB' and @value='20916']",".//*[@id='FmFm1_Ctrl16_20916_Ctrl16_TB']"),
                      'Withdrawn': (".//*[@name='Fm1_Ctrl16_LB' and @value='20922']",".//*[@id='FmFm1_Ctrl16_20922_Ctrl16_TB']"),
                      'Expired': (".//*[@name='Fm1_Ctrl16_LB' and @value='20917']",".//*[@id='FmFm1_Ctrl16_20917_Ctrl16_TB']"),
                      'Terminated': (".//*[@name='Fm1_Ctrl16_LB' and @value='20921']",".//*[@id='FmFm1_Ctrl16_20921_Ctrl16_TB']"),
                      'Incomplete': (".//*[@name='Fm1_Ctrl16_LB' and @value='23706']",".//*[@id='FmFm1_Ctrl16_23706_Ctrl16_TB']")
                      }
        for oStatus in lstStatus:
            #get the xpaths
            xPaths = dictStatus[oStatus[0]]
            xpChk = xPaths[0] #get the xpath to the check box
            xpTxt = xPaths[1] #get the xpath to the textbox
            elemChk = self._driver.find_element_by_xpath(xpChk)
            #now check/uncheck as needed
            if elemChk.is_selected() != oStatus[1]:
                elemChk.click()
            if elemChk.is_selected(): #when it's selected, populate the date range
                elemTxt = self._driver.find_element_by_xpath(xpTxt)
                elemTxt.clear()
                elemTxt.send_keys(oStatus[2])

        xpSelect = ".//*[@id='Fm1_Ctrl129_LB']"  #this is the xpath to find the select element
        elemSelect = self._driver.find_element_by_xpath(xpSelect)
        for option in elemSelect.find_elements_by_tag_name('option'):
            if strPropType == option.text:
                option.click()


        xPath = ".//*[@id='Fm1_Ctrl19_TextBox']"
        elemZip = self._driver.find_element_by_xpath(xPath)
        elemZip.send_keys(strZip)
        time.sleep(2)
        ##get the result link and result count
        xpResultCntLnk = ".//*[@id='m_ucSearchButtons_m_clblCount']"
        xpResultLnk = ".//*[@id='m_ucSearchButtons_m_lbSearch']"
        elemResulCnttLnk = self._driver.find_element_by_xpath(xpResultCntLnk)

        nResultCount = int(re.findall(r'\d+', elemResulCnttLnk.text)[0])
        if nResultCount> 0:
            #first get the list of files that exists in the results folder, get the MLS numbers in a list
            jsonPath = self._cfg.getConfigValue("JsonPath")
            lstMLS = [ s.lstrip(jsonPath + "\\").rstrip(".json") for s in glob.glob("{0}\\*.json".format(jsonPath))]

            elemResultLnk = self._driver.find_element_by_xpath(xpResultLnk)
            nTryCount = 0
            while True:
                elemResultLnk.click()
                #time.sleep(2)
                xpMLSHeader = ".//th[@data-mlheader='1\\bMLS #']"
                try:
                    elemMLSHeader = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, xpMLSHeader)))
                    break
                except:
                    nTryCount+=1
                    if nTryCount <10:
                        self._driver.back()
                    else:
                        return False
                #now click the first in search result:
            xpMLSs = ".//td[@class='d1m5']/span[@class='d1m1']"
            elemMLSs = self._driver.find_elements_by_xpath(xpMLSs)
            xpTester = ".//div[@class='tabSelected']"
            nTryCount = 0
            bSearchStarted = False #it's a flag that tells if a new search has started
            while True:
                #find the first mls link that hasn't be searched
                for item in elemMLSs:
                    strMLS = item.text
                    if strMLS not in lstMLS:
                        #if the mls is not in the existing list, go ahead and start normal scraping
                        elemMLSs[0].click()
                        bSearchStarted = True
                        try:
                            elemTest = WebDriverWait(self._driver,10).until(EC.presence_of_element_located((By.XPATH, xpTester)))
                            break
                        except:
                            nTryCount +=1
                            if nTryCount <10:
                                self._driver.back()
                            else:
                                return False
                if not bSearchStarted: #if it still hasn't found a unprocessed mls, try to flip to next page
                    #look for the "next" tag to click
                    xpNextOrPrev = ".//a[contains(@href, 'javascript:__doPostBack('m_DisplayCore','Redisplay|,,']"
                    elems = self._driver.find_elements_by_xpath(xpNextOrPrev)
                    for elem in elems:
                        if elem.text == 'Next':
                            #click the next link
                            elem.click()
                            time.sleep(2)


            ##click the result search
            while True:
                #get the lat/lon
                xpMap = ".//a[@title='View Map']"
                elemMap = self._driver.find_element_by_xpath(xpMap)
                latlon = self.GetLatLong(elemMap)
                elemNext = self.ScrapSearchResultsPropertyDetailPage(strPropType, latlon)
                if elemNext is None:
                    break
                else:
                    elemNext.click()
                    time.sleep(1)
        return True

    def GetLatLonFromPropDetailPage(self):
        xpViewMap = "//a[@title='View Map']"
        elemViewMap = self.find_wait_get_element('xpath',xpViewMap,False,15)
        if elemViewMap is not None:
            return self.GetLatLon(elemViewMap, False)
        else:
            return (None, None)


    '''get the lat lon information'''
    def GetLatLon(self, elemMap, bSaveJson = False):

        if elemMap is not None:
            window_before = self._driver.window_handles[0]
            try:
                elemMap.click()
            except:
                traceback.print_exc()
                # if it throw exception, returns (None, None) as lat lon
                return [None, None]
            time.sleep(1)
            # self.wait_for_new_window(self._driver)
            window_after = self._driver.window_handles[1]
            self._driver.switch_to.window(window_after)
            xpLatLon = ".//input[@id='m_ucStreetViewService_m_hfParams']"
            elemLatLon = self._driver.find_element_by_xpath(xpLatLon)
            strLatLon = elemLatLon.get_attribute('value')
            latlon = re.findall(r'[-+]?\d+\.\d+', strLatLon)[:2]
            self._driver.close()
            self._driver.switch_to.window(window_before)
            return latlon

    '''
    return value: the next element for the calling page to click, if there is no next element, return None
    '''
    def ScrapSearchResultsPropertyDetailPage(self, strPropType, latlon):
        xpNext = ".//a[@id='m_DisplayCore_dpy3']"
        try:
            elemNext = self._driver.find_element_by_xpath(xpNext)
        except:
            elemNext = None

        strHtml = self._driver.page_source
        self.ScrapSearchResultPropertyHtml(strHtml, strPropType, latlon)
        return elemNext
    '''
        hWindow is the handle of the window
    '''
    def ScrapResultPageDetails(self):
        strHtml = self._driver.page_source
        self.ScrapSearchResultPropertyHtml(strHtml, strPropType)



    '''
    strip the value out of the source text based on wild cards
    '''
    def depricated_StripWildCards(self, strSourceText, strDataType, strTextFormatStrings):
        if len(strSourceText) == 0:
            return None
        try:
            patts = strTextFormatStrings.split('|')
            val = None
            for patt in patts:
                try:
                    print(re.match(patt, strSourceText).groups())
                    val = re.match(patt, strSourceText).groups(1)[0]
                    if val is None:
                        return None
                    else:
                        break
                except:
                    continue
            #patt = re.compile(strTextFormatStrings)
            #print(re.match(patt, strSourceText).groups())
            #val = re.match(patt, strSourceText).group(1)
            if strDataType == 'int':
                val = val.replace(',','')
                return int(val)
            elif strDataType == 'string':
                return val
            elif strDataType == 'currency':
                if val[0] == '$':
                    val = val[1:]
                val=val.replace(',','')
                return int(val)
            else:
                print("The data type: {0} is unknown, unable to parse {1}".format(strDataType, strSourceText))
                return None
        except:
            print("Error when trying to parse {0}".format(strSourceText))
            return None

    '''
        Property type       Content
        SFH                 d48m2
        Rent                d82m2
        Condo               D76m2
        Multi - fam         D93m2
        Lot                 D91m2
    '''

    def depricated_ScrapSearchResultPropertyHtml(self, strHtml, strPropType, latlon):
        '''
        scrapes the contents of the property search results page
        strHtml: the html content as a string.
        '''
        soup = bs(strHtml, 'lxml')
        # extract all tables' contents 'Single-Family', 'Townhouse/Condo','Lots','Multi-Family','Rental'
        if strPropType == 'Single-Family':
            nCode = 48

        elif strPropType == 'Rental':
            nCode = 82
        elif strPropType == 'Lots':
            nCode = 91
        elif strPropType == 'Townhouse/condo':
            outputFile = open(pathHtml + "\\" + str(i)+".html","w")
            outputFile.write(self._driver.page_source)
            outputFile.close()
            nCode = 76
        elif strPropType == 'Multi-Family':
            nCode = 93
        else:
            return False
        strProp = 'd{0}m2'.format(nCode)
        tables = soup.find_all('table',{'class':strProp})
        if len(tables) == 0:
            return False
        strPrevElem = ''
        #scrape the page and put the content in a list
        lstScrapeResults = []
        strMLS = ''
        for td in tables[0].find_all('td'):
            lst = td.find_all('table')
            if len(lst) ==0:
                strCurElem =td.text.strip().replace(u'\xa0', u' ')
                if len(strCurElem) == 0: # we need to make sure there is no nested table within the td
                    if strPrevElem != '' and strPrevElem[-1] == ':':
                        #print(strCurElem)
                        lstScrapeResults.append(strCurElem)
                        strPrevElem = strCurElem
                else:
                    #print(strCurElem)
                    strPrevElem = strCurElem
                    lstScrapeResults.append(strCurElem)
        #now read the sections and columns to scrape and search through the list
        lstPropSections = self._cfg.getConfigValues("PageContents/Section")
        #iterate through each section
        oJResult = [] #the result object to be written to Json
        for sect in lstPropSections:
            oSectionResult = {}
            strSectName = sect['name']
            strSectTitle = sect['Title']
            if strSectTitle == '':
                nStartIdx =0
            else:
                try:
                    nStartIdx = lstScrapeResults.index(strSectTitle)
                except:
                    print("Section {0} not found!".format(strSectTitle))
                    continue
            oSectionResult.update({'SectionName': strSectName})
            dictColumns = {}
            lstColumns = self._cfg.getConfigValues('PageContents/Section[@name="{0}"]/Column'.format(strSectName), True)
            for oColumn in lstColumns:
                strColumnName = oColumn['name']
                strDataType = oColumn['DataType']
                strText = oColumn['Text']
                try:
                    strFormatString = oColumn['Format']
                except:
                    strFormatString = ''
                nColumnIdx = -1
                try: # it will throw an exception if text is not found
                    nColumnIdx = lstScrapeResults[nStartIdx:].index(strText.strip())
                    strColumnText = lstScrapeResults[nStartIdx:][nColumnIdx+1]
                except:
                    print("Unable to find the value corresponding to field: {0}".format(strText))
                    dictColumns.update({strColumnName:None})
                    continue

                #update 4/23/2018: here we will not check the data type, and treats everyone as string
                dictColumns.update({strColumnName: strColumnText})
                '''
                if strDataType == 'string':
                    if strFormatString == '':
                        dictColumns.update({strColumnName:strColumnText})
                    else:
                        temp = self.StripWildCards(strColumnText, strFormatString,strFormatString)
                        dictColumns.update({strColumnName:temp})
                elif strDataType == 'currency':
                    try:
                        dVal = float(strColumnText.strip().strip('$').replace(',',''))
                        dictColumns.update({strColumnName:dVal})
                    except:
                        print('Failure to convert {0} from currency to float'.format(strColumnText))
                        dictColumns.update({strColumnName:-1})
                elif strDataType == 'int':
                    if strFormatString == '':
                        if len(strColumnText) == 0:
                            dictColumns.update({strColumnName:None})
                        else:
                            try:
                                nVal = int(strColumnText.strip().replace(',', ''))
                                dictColumns.update({strColumnName: nVal})
                            except:
                                if strColumnText.strip().replace(',', '') == '':
                                    dictColumns.update({strColumnName: None})
                                else:
                                    print('Failure to convert {0} from string to int'.format(strColumnText))
                                    dictColumns.update({strColumnName: -1})
                    else:
                        nVal = self.StripWildCards(strColumnText, strDataType, strFormatString)
                        dictColumns.update({strColumnName:nVal})
                elif strDataType == 'date':
                    if len(strColumnText) == 0:
                        dictColumns.update({strColumnName: None})
                    else:
                        try:
                            dVal = date.strptime(strColumnText, '%m/%d/%H')
                            dictColumns.update({strColumnName: dVal})
                        except:
                            print('Failure to convert {0} from string to date'.format(strColumnText))
                            dictColumns.update({strColumnName: None})
                else:
                    pass
                '''
            #now get mls number, if exists
            try:
                strMLS = dictColumns["MLSNum"]
            except:
                pass
            dictColumns.update({"MLSNum":strMLS})
            if strSectTitle == '':
                #if section title = '', add lat lon information
                #dictColumns.update({'lat':float(latlon[0])})
                #dictColumns.update({'lon': float(latlon[1])})
                dictColumns.update({'lat':latlon[0]})
                dictColumns.update({'lon': latlon[1]})
            oSectionResult.update({"Details":dictColumns})
            oJResult.append(oSectionResult)
        jsonPath = self._cfg.getConfigValue("JsonPath")
        with open('{0}\\{1}.json'.format(jsonPath,strMLS), 'w') as outfile:
            json.dump(oJResult, outfile)

        return oJResult

if __name__ == "__main__":
    print("Start scrapping")
    o = cMatrixScrapper("AllPropScrapper", "DEV")
    o.SignIntoMatrix()
    strZip = '77096'
    datFrom = date(2018,1,1)
    datTo =  date(2018,10,1)
    strMLS = '72016589'

    nRecCount = o.QuerySoldAllPropClassicByZip(datFrom, datTo, strZip)
    nRecCount = o.ProcessAllPropClassicSearchResultsPage(nRecCount, True)

    nRecCount = o.QueryPropertyByMLS(strMLS,False, True)
    nRecCount = o.ProcessAllPropClassicSearchResultsPage(nRecCount,False)
    (lat, lon) = o.GetLatLonFromPropDetailPage()
    print('Lat={0}, Lon={1}'.format(lat, lon))