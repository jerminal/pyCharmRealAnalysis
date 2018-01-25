import XmlConfigReader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import re

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


    def ScrapeAllPropPage(self, lstSearchCriteria):
        '''
             sccrape all property page based on input
             oSearchCriteria: [(by, ByType, ControlType, Value, Description)]
             example('ID', 'idab379', 'checkbox', True, 'checkbox for blah blah')
        '''
        # load the page
        strPageLink = "http://matrix.harmls.com/Matrix/Search/AllProperties/Classic"
        self._driver.get(strPageLink)
        #verify the page load completes by checking existance of the first search creteria

        # Load searh criteria, if an element is not found, it returns with False and with a string explanation of the error
        for criteria in lstSearchCriteria:
            if criteria[2] == 'checkbox':
                pass
            elif criteria[2] == 'textbox':
                pass


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
        lstScrapeResults = []
        for td in tables[0].find_all('td'):
            lst = td.find_all('table')
            if len(lst) ==0:
                strCurElem =td.text.strip()
                if len(strCurElem) == 0: # we need to make sure there is no nested table within the td
                    if strPrevElem != '' and strPrevElem[-1] == ':':
                        print(strCurElem)
                        lstScrapeResults.append(strCurElem)
                        strPrevElem = strCurElem
                else:
                    print(strCurElem)
                    strPrevElem = strCurElem
                    lstScrapeResults.append(strCurElem)

        #tag = tables[0].find('span', text = 'ML#: ')
        #strMLS = tag.parent.next_sibling.next_sibling.text
        #first search for a table with class tag that's the following:
        '''
        Property type       Content
        SFH                 d48m2
        Rent                d82m2
        Condo               D76m2
        Multi - fam         D93m2
        Lot                 D91m2
        '''
        #

        return True

if __name__ == "__main__":
    print("Start scrapping")
    o = cMatrixScrapper("AllPropScrapper", "DEV")
    file = '..\\testData\\sfh.html'
    with open(file, 'r') as s:
        sHtml = s.read()
    o.ScrapSearchResultPropertyDetail(sHtml, 'sfh')