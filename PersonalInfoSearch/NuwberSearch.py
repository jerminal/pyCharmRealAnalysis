import json
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class NuwberSearch:
    def __init__(self):
        # initialize selenium
        executable_path = r"C:\Python35\selenium\webdriver\firefox\x86\geckodriver.exe"
        binaryPath = "C:\\Program\\Files(x86)\\Mozilla\\Firefox\\firefox.exe"
        self._driver = webdriver.Firefox(executable_path=executable_path)
        #the result in a dictionary, key:(first name, last name, address) value:(age, phone)
        self._dictRslt = {}
        self.readDictFile()

    def searchNameAndAddress(self, firstN, lastN, addr):
        if (firstN, lastN, addr ) not in self._dictRslt:
            # driver = webdriver.Firefox(firefox_binary=binary)
            print("load {0} and start google search".format("http://www.google.com"))
            self._driver.get("http://www.google.com")
            #locate the input box
            elemInput = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
            elemInput.clear()
            #put in the search keywords
            elemInput.send_keys(firstN + " " + lastN + " " + addr )

            #trigger google saerch
            try:
                elemSearch = self._driver.find_element_by_name("btnK")
                elemSearch.click()
                time.sleep(2)
            except:
                #print("{0} {1} on {2} not found by Nuwber.com".format(firstN, lastN, addr))
                #return
                pass
            #get the desired search result
            try:
                #elemNuwberResult = self._driver.find_element_by_partial_link_text("Nuwber")
                elemNuwberResult = self._driver.find_element_by_xpath("//a[contains(@href, 'nuwber.com')]")
            except:
                print("{0} {1} on {2} not found by Nuwber.com".format(firstN, lastN, addr))
                return
            #load nuwber webpate
            elemNuwberResult.click()
            time.sleep(2)
            self.scrapNuwberResultPageDetails(1)
            self.writeResultToFile()
        else:
            print('{0} {1} on {2} exists in dictionary. Skip'.format(firstN, lastN, addr))
    def writeResultToFile(self):
        path = 'result.txt'
        with open(path, 'a') as f:
            #json.dump(self._dictRslt, f)
            for k,v in self._dictRslt.items():
                line = "{0},{1},{2},{3}".format(k[0], k[1], k[2],v)
                print(line, file=f)
    def readDictFile(self):
        path = 'result.txt'
        with open(path, "r") as f:
            for line in f:
                k_v = line.split(',')
                v = list(map(lambda x: x.strip(" "), k_v))
                self._dictRslt[tuple(v[:3])] = v[3]

    def scrapNuwberAddressRangePage(self):
        lstElemAddr = self._driver.find_elements_by_css_selector("div[class='panel panel-default house']")
        for elm in lstElemAddr:
            #find each address and its owner's information
            elmAddr = elm.find_element_by_css_selector("h3[class='panel-title']")
            strAddr = elmAddr.text
            #find each owner:
            elmPersons = elm.find_elements_by_css_selector("a[class='person']")
            for elmPerson in elmPersons:
                strName = elmPerson.text
                lnkPerson = elmPerson.get_attribute("href")
                print("found {0} on {1}".format(strName, strAddr))
                #now let's start launch new windows one by one
                current_window = self._driver.current_window_handle
                # open a new window with the link
                self._driver.execute_script("window.open(arguments[0]);", lnkPerson)
                # switch to the new window
                new_window = [window for window in self._driver.window_handles if window != current_window][0]
                self._driver.switch_to.window(new_window)
                # do scrapping
                time.sleep(3)
                self.scrapNuwberResultPageDetails(2)
                # close the new window
                self._driver.close()
                # swtich back to the old window
                self._driver.switch_to.window(current_window)


    def scrapNuwberResultPageDetails(self, nRecursiveLevel):
        try:
            elemName = self._driver.find_element_by_id("name")
        except:
            #it is not a ligit search result, now it should show adddress range, then scrap address range page:
            self.scrapNuwberAddressRangePage()
            return
        result_first_name = elemName.get_attribute("data-fn")
        result_last_name = elemName.get_attribute("data-ln")
        elemAge = self._driver.find_element_by_css_selector("div.mb10-xs")
        age = elemAge.text
        #now find address
        elemAddr = self._driver.find_element_by_xpath("//meta[@itemprop='streetAddress']")
        result_addr = elemAddr.get_attribute("content")

        #add result to dictionary
        if (result_first_name, result_last_name, result_addr) not in self._dictRslt:
            print("Adding {0} {1} on {2}, age:{3} to dictionary".format(result_first_name, result_last_name, result_addr, age))
            self._dictRslt[(result_first_name.strip(' '), result_last_name.strip(' '), result_addr.strip(' '))] = (age,)
        else:
            print("{0} {1} on {2} already exist in dictionary. skip".format(result_first_name, result_last_name, result_addr))
        # now find the neighbors on the same street
        if nRecursiveLevel<=1:
            elemNeighbors = self._driver.find_elements_by_css_selector("a.neighbour")
            lstNeighborsUrl = []
            for neighbor in elemNeighbors:
                strUrl = neighbor.get_attribute("href")
                elmNbrName = neighbor.find_element_by_css_selector("p.mb0")
                elmNbrAddr = neighbor.find_element_by_css_selector("p[class='mb0 nounderline']")
                txtNbrName = elmNbrName.text
                txtNbrAddr = elmNbrAddr.text
                temp_firstName = txtNbrName.split(' ')[0]
                temp_lastName = txtNbrName.split(' ')[-1]
                if (temp_firstName, temp_lastName, txtNbrAddr) not in self._dictRslt:
                    lstNeighborsUrl.append(neighbor.get_attribute("href") )

                    if nRecursiveLevel<=1:
                        current_window = self._driver.current_window_handle
                        #open a new window with the link
                        self._driver.execute_script("window.open(arguments[0]);", strUrl)
                        #switch to the new window
                        new_window= [window for window in self._driver.window_handles if window != current_window][0]
                        self._driver.switch_to.window(new_window)
                        #do scrapping
                        time.sleep(3)
                        self.scrapNuwberResultPageDetails(2)
                        #close the new window
                        self._driver.close()
                        #swtich back to the old window
                        self._driver.switch_to.window(current_window)
                        #neighbor.click()


if __name__ == "__main__":
    #program entry here
    #GALLOWAY ROBERT E	10206 BALMFORTH LN
    o = NuwberSearch()
    path = "owner_list.txt"
    with open(path, "r") as f:
        n=0
        for line in f:
            v = line.split(',')
            print("{0}: Searching {1} {2} on {3}".format(n, v[0], v[1], v[2]))
            o.searchNameAndAddress(v[0], v[1], v[2])
            n+=1
    #o.searchNameAndAddress("FELICIA", "WORKENEH", "4718 Imogene st")


