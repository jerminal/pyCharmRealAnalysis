import XmlConfigReader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import re
from datetime import date
import json

class cMatrixScrapper:
    def __init__(self, strConfigFilePath, strConfigSect ):
        #initialize the object, and connect to har
        print("Initialize Matrix scrapper")
        self._cfg = XmlConfigReader.Config(strConfigFilePath, strConfigSect)
        executable_path = self._cfg.getConfigValue("GeckoPath")
        strBrowser = self._cfg.getConfigValue("Browser")
        print("Opening {0} browser".format(strBrowser))

        #if strBrowser == "Chrome":
        #    self._driver = webdriver.Chrome()
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

        (elemNextLnk, nFailureCnt) = self.find_wait_get_element("link_text", "Enter Matrix MLS")
        window_before = self._driver.window_handles[0]
        xpath = "/html[@class='wf-effra-n4-active wf-effra-n7-active wf-effra-n3-active wf-effra-n5-active wf-effra-n9-active wf-active']/body/div[@class='content overlay']/div[@class='container']/div[@class='rightPane']/div[@class='box_simple gray agentbox newhar']/div[@class='box_content grid_view']/a[1]"
        (elemNextLnk, nFailureCnt) = self.find_wait_get_element("xpath", xpath, True)
        time.sleep(3)

        self.wait_for_new_window(self._driver)
        window_after = self._driver.window_handles[1]
        self._driver.close()
        self._driver.switch_to.window(window_after)
        print("signed in")
        return True


    def wait_for_new_window(self, timeout=10):
        handles_before = self._driver.window_handles
        yield
        WebDriverWait(self._driver, timeout).until(
            lambda driver: len(handles_before) != len(driver.window_handles))

    '''
    find, wait and get element, if not successful, it will keep on trying for 10 times before quit the program
    '''
    def find_wait_get_element(self,elementType, val, bClick=False):
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
        get a list of inputs and run the scrapper item by item in the list
    '''
    def RunJob(self):
        # get the last date scrapper worked

        # calculate date range, chop into pieces if necessary


        # get the list of zip codes to scrap

        # get the list of property types to scrap

        # Loop and scrape each combination
        # Scrape all Property Matrix Classic
        bResult = False
        while bResult == False:
            bResult = self.ScrapeAllPropPage()

        '''
             sccrape all property page based on input
             oStatus: [(text, value(true, false),date_range_as_string)]; example('Active', False, '7/31/2003-9/1/2003')
            lstPropType: ['Single-Family', 'Townhouse/Condo','Lots','Multi-Family','Rental']
            ZipCode: 
            City
            
        '''
    def RunAllPropPage(self, lstStatus, lstPropType, ZipCode,City):
        """

        :rtype: object
        """
        # load the page
        strPageLink = "http://matrix.harmls.com/Matrix/Search/AllProperties/Classic"
        self._driver.get(strPageLink)
        #verify the page load completes by checking existance of the first search creteria

        # Load searh criteria, if an element is not found, it returns with False and with a string explanation of the error
        for oStatus in lstStatus:
            
        # Run search

        ##get the result link and result count
        ##click the result search

        #Load the result page

        #Iterate through all results
        ##Look for the "Next" link on the bottom right of the page, if found set variable to True
        urlNextPage = "something"
        while urlNextPage is not None:
            ##first iterathrough each MLS Link
            ### Look for the next MLS Link, if found, scrape Property result page
            ##Increase the result scrapped counter
            ### else, look for the next page link:
            if True:
                urlNextPage = "something"
            else:
                urlNextPage = None
        #at the end, compare scrapped results and search results count
        return True

    '''
    strip the value out of the source text based on wild cards
    '''
    def StripWildCards(self, strSourceText, strDataType, strTextFormatStrings):
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

    def ScrapSearchResultPropertyDetail(self, strHtml, strPropType):
        '''
        scrapes the contents of the property search results page
        strHtml: the html content as a string.
        '''
        soup = bs(strHtml, 'lxml')
        # extract all tables' contents
        if strPropType == 'sfh':
            nCode = 48

        elif strPropType == 'rnt':
            nCode = 82
        elif strPropType == 'lot':
            nCode = 91
        elif strPropType == 'th':
            nCode = 76
        elif strPropType == 'mlt':
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
            #now get mls number, if exists
            try:
                strMLS = dictColumns["MLSNum"]
            except:
                pass
            dictColumns.update({"MLSNum":strMLS})
            oSectionResult.update({"Details":dictColumns})
            oJResult.append(oSectionResult)

        with open('..\\testData\\Result\\result.json', 'w') as outfile:
            json.dump(oJResult, outfile)

        return oJResult

if __name__ == "__main__":
    print("Start scrapping")
    o = cMatrixScrapper("AllPropScrapper", "DEV")
    o.SignIntoMatrix()
    oSearchCriteria = [(),()]
    '''
    the following part tests the html search results 
    '''
    '''
    file = '..\\testData\\sfh.html'
    with open(file, 'r') as s:
        sHtml = s.read()
    o.ScrapSearchResultPropertyDetail(sHtml, 'sfh')

    file = '..\\testData\\rnt.html'
    with open(file, 'r') as s:
        sHtml = s.read()
    o.ScrapSearchResultPropertyDetail(sHtml, 'rnt')

    file = '..\\testData\\lot.html'
    with open(file, 'r') as s:
        sHtml = s.read()
    o.ScrapSearchResultPropertyDetail(sHtml, 'lot')
    '''

