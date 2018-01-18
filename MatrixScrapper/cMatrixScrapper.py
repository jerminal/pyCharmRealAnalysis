import XmlConfigReader
from selenium import webdriver

class cMatrixScrapper:


    def __init__(self, strConfigFilePath, strConfigSect ):
        #initialize the object, and connect to har
        self._cfg = XmlConfigReader.Config(strConfigFilePath, strConfigSect)
        strUserName = self._cfg.getConfigValue("HARUserName")
        strPwd = self._cfg.getConfigValue("HARPassword")
        strEntryUrl = self._cfg.getConfigValue("EntryUrl")
        executable_path = self._cfg.getConfigValue("GeckoPath")
        strBrowser = self._cfg.getConfigValue("Browser")
        if strBrowser == "Chrome":
            self._driver = webdriver.chrome
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

    def SignInToMatrix():
        return True

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


    # sccrape all property page based on input
    def ScrapeAllPropPage(self):
        # load the page

        # Load searh criteria

        # Run search

        # Run through search results


        return True

    def ScrapSearchResultPage(self):
        return True

if __name__ == "__main__":
    print("Start scrapping")
