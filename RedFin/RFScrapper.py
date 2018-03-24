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
    def __init__(self, strConfigAppName, strConfigSect):
        #load redfind website
        self._cfg = XmlConfigReader.Config(strConfigAppName, strConfigSect)
        strBrowser = self._cfg.getConfigValue("Browser")
        print("Opening {0} browser".format(strBrowser))

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
        try:
            elemSignin = self._driver.find_element_by_xpath(xpSignin)
            #load the sign page
            elemSignin.click()
            time.sleep(2)
            xpTemp = ".//button[@class='button Button  tertiary emailSignInButton v3']"
            elemContinuewEmail = self._driver.find_element_by_xpath(xpTemp)
            elemContinuewEmail.click()
            time.sleep(1)
            xpEmail = ".//input[@type='email' and @name='emailInput']"
            xpPwd =".//input[@type='password' and @name='passwordInput']"
            xpSignin = ".//button[@type='submit' and @data-rf-test-name='submitButton']"
            elemEmail = self._driver.find_element_by_xpath(xpEmail)
            elemPwd = self._driver.find_element_by_xpath(xpPwd)
            elemSignin  = self._driver.find_element_by_xpath(xpSignin)

            #start sign in
            strUsr = self._cfg.getConfigValue("UsrName")
            strPwd = self._cfg.getConfigValue("Password")
            elemEmail.send_keys(strUsr)
            elemPwd.send_keys(strPwd)
            elemPwd.send_keys(Keys.RETURN)

        except:
            #sign in not exist, which means you are already signed in
            pass

        return True

    def SearchZip(self, strZip, datFrom, datTo, strPropType, bForSale, bSold):
        #first fill in the zip code
        xpSearchBox = ".//input[@type='search' and @id='search-box-input']"
        elemSearchBox = self._driver.find_element_by_xpath(xpSearchBox)
        elemSearchBox.send_keys(strZip)
        elemSearchBox.send_keys(Keys.RETURN)
        time.sleep(1)
        # click "filter" button
        xpFilter = ".//button[@class='button Button  wideSidepaneFilterButton v3 compact text']"
        elemFilter = self._driver.find_element_by_xpath(xpFilter)
        elemFilter.click()
        # select property type
        dictPropType = { 'SFH' : ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt1']", 'Condo': ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt2']",'BCD': '".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt3']",'ABC': xpMF = ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt4']"}



if __name__ == "__main__":
    oRF = RFScrapper("RedFin","DEV")
