import XmlConfigReader
import csv
import os
import pymysql
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
        xpSignin = ".//button[@type='button' and @data-rf-test-name='SignInLink']"
        try:
            #elemSignin = self._driver.find_element_by_xpath(xpSignin)
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

    '''load the csv file downloaded from redfin to mysql db'''
    def LoadCSVToMySqlDB(self, strPath):
        host = self._cfg.getConfigValue(r'MySQL/host')
        port = int(self._cfg.getConfigValue(r"MySQL/port"))
        user = self._cfg.getConfigValue(r"MySQL/user")
        passwd = self._cfg.getConfigValue(r"MySQL/password")
        db = self._cfg.getConfigValue(r"MySQL/DB")
        cnn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
        print('database connected')
        cur = cnn.cursor()
        sqlInsert = "INSERT INTO Redfin_History (`SALE TYPE`,`SOLD DATE`,'PROPERTY TYPE`,`ADDRESS`,`CITY`,`STATE`,`ZIP`,`PRICE`,`BEDS`,`BATHS`,`LOCATION`,`SQUARE FEET`,`LOT SIZE`,`YEAR BUILT`,`DAYS ON MARKET`,`$/SQUARE FEET`,`HOA/MONTH`,`STATUS`,`NEXT OPEN HOUSE START TIME`,`NEXT OPEN HOUSE END TIME`,`URL`,`SOURCE`,`MLS#`,`FAVORITE`,`INTERESTED`,`LATITUDE`,`LONGITUDE`) " \
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sqlUpdate = "UPDATE Redfin_History set `SALE TYPE`=%s,`SOLD DATE`=%s,'PROPERTY TYPE`=%s,`ADDRESS`=%s,`CITY`=%s,`STATE`=%s,`ZIP`=%s,`PRICE`=%s,`BEDS`=%s,`BATHS`=%s,`LOCATION`=%s,`SQUARE FEET`=%s,`LOT SIZE`=%s,`YEAR BUILT`=%s," \
                    "`DAYS ON MARKET`=%s,`$/SQUARE FEET`=%s,`HOA/MONTH`=%s,`STATUS`=%s,`NEXT OPEN HOUSE START TIME`=%s,`NEXT OPEN HOUSE END TIME`=%s,`URL`=%s,`SOURCE`=%s,`FAVORITE`=%s,`INTERESTED`=%s,`LATITUDE`=%s,`LONGITUDE`=%s WHERE ,`MLS#`=%s"

        lstFiles = [f for f in os.listdir(strPath) if f[:6] == 'redfin']
        for f in lstFiles:
            csvData = csv.reader(file(f))
            for row in csvData:
                cur.execute(sqlInsert, row)


        return


    def GetDownloadPath(self):
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'downloads')


    def Easy_SearchZip(self, strZip, strPastPeriod, lstPropType, bForSale, bSold):
        strProp = '+'.join(lstPropType)
        strProp = re.sub('-','',strProp.lower())
        url = "https://www.redfin.com/zipcode/{0}/filter/{1},include=sold-1mo".format(strZip, strProp)
        self._driver.get(url)
        time.sleep(2)
        xpDownload =".//a[@id='download-and-save' and @class='downloadLink']"
        elemDownload= self._driver.find_element_by_xpath(xpDownload)
        elemDownload.click()


    def SearchZip(self, strZip, strPastPeriod, lstPropType, bForSale, bSold):
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
        dictPropType = { "House" : ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt1']",
                         "Condo" : ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt2']",
                         "Townhouse" : ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt3']",
                         "Multi-Family" : ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt4']",
                         "Land": ".//button[@class='button Button plain  icon unpadded propertyTypeButton' and @data-rf-test-name='uipt5']"
                         }

        for prop in lstPropType:
            try:
                xpPropType = dictPropType[prop]
                elemPropType = self._driver.find_element_by_xpath(xpPropType)
                elemPropType.click()
            except:
                print("Error locating element:{0}".format(prop))


        #xpSale = ".//input[@name='showForSaleToggle' and @type='checkbox']"
        xpSale = ".//span[@data-rf-test-name='Toggle' and @class='field Toggle styled v97']"
        elemSale = self._driver.find_element_by_xpath(xpSale)
        elemSale.click()
        '''
        if elemSale.get_attribute("value") == 'on':
            bStatus = True
        else:
            bStatus = False
        if bStatus != bForSale:
            elemSale.click()
        '''
        time.sleep(0.5)
        xpBeforeSoldPeriod = ".//span[@class='mounted field select Select clickable solds' and @data-rf-test-name='Select']"
        elemBeforeSoldPeriod = self._driver.find_element_by_xpath(xpBeforeSoldPeriod)
        elemBeforeSoldPeriod.click() #this makes the options visible
        xpSoldPeriod = ".//select[@name='solds'  and @class='select']"
        elemSelectPeriod = self._driver.find_element_by_xpath(xpSoldPeriod)
        for option in elemSelectPeriod.find_elements_by_tag_name('option'):
            if option.get_attribute('value') == strPastPeriod:
                option.click()



        xpSold = ".//input[@name='showSoldsToggle' and @type='checkbox']"
        elemSold = self._driver.find_element_by_xpath(xpSold)
        if elemSold.get_attribute("value") == 'on':
            bStatus = True
        else:
            bStatus = False
        if bStatus != bSold:
            elemSold.click()
        time.sleep(0.5)

        xpSoldDateRange = ".//span[@class='mounted field select Select clickable Focused dijitFocused solds']"
        elemSoldDateRange = self._driver.find_element_by_xpath(xpSoldDateRange)

        

if __name__ == "__main__":
    oRF = RFScrapper("RedFin","DEV")

    lstPropType = ['House', 'Condo','Townhouse','Multi-Family','Land']
    dictSoldDateRange = {'Last 1 month':'30', 'Last 1 week':'7', 'Last 3 months':'90', 'Last 6 months':'180', 'Last 1 year':'365', 'Last 2 years':'730', 'Last 3 years':'1095', 'All':'36500'}
    oRF.Easy_SearchZip('77007',dictSoldDateRange['Last 1 month'],lstPropType, False, True)