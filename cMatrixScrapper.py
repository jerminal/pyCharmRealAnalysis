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
    def QueryAllPropClassicPage(self, lstParams):

        return

    '''
        scrapes a a property page and returns a dictionary containing the property details data
    '''

    def ScrapPropDetailsPage(self, strMLS):
        dict = {}
        #1: go to the matrix all property classic page and fill in the mls number

        #2: choose to view details when viewing results

        #3: scrap the details

        return dict

    def scrapNewProperty(self, datStart, datEnd, strPropType):
        return

    def scrapSoldProperty(self, datStart, datEnd, strPropType):
        return

if __name__ == "__main__":
    o = MatrixScrapper("AllPropScrapper", "DEV")
