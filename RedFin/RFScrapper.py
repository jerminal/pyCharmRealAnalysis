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

class RFScrapper:
    def __init__(self, ):
        #load redfind website
        strBrowser = "Chrome"
        if strBrowser == "Chrome":
            self._driver = webdriver.Chrome()
        self.SignIntoRF()


    def SignIntoRF(self):
        # driver = webdriver.Firefox(firefox_binary=binary)
        self._driver.get('http://www.redfin.com')  # load the web page
        #wait for the 800 number to verify the page is loaded:
        #<span class="phoneNumberDigits">1-844-759-7732</span>


        #look for the sign in button, if it exists it means user needs to sign in:
        #< button         type = "button"    class ="button Button compact text" tabindex="0" data-rf-test-name="SignInLink" > < span > Sign In < / span > < / button >
        xpSignin = ".//button[@data-rf-test-name='SignInLink']"

        '''
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
        
        '''
        return True


if __name__ == "__main__":
    oRF = RFScrapper()
