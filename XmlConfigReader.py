from bs4 import  BeautifulSoup
import lxml.etree
import os

class Config:
    def __init__(self, AppName, Inst):
        self._dir = os.getcwd() + r'\RealAnalysisConfig.xml'
        #print (self._dir)
        #self._soup = BeautifulSoup(self._dir, 'lxml')
        self._doc = lxml.etree.parse(self._dir)
        self._App = AppName
        self._Inst = Inst
    def getConfigValue(self, partialPath):
        xpath = "//data/Application[@name='{0}']/{1}/{2}/text()".format(self._App, self._Inst, partialPath)
        #print(xpath)
        #val = self._doc.xpath("//data/Application[@name='{0}']/{1}/{2}/text()".format(self._App, self._Inst, partialPath))
        #print(val)
        #xpath = "//Application[@name='{0}']/{1}/{2}/text()".format(self._App, self._Inst, partialPath)
        #print(xpath)
        val = self._doc.xpath(xpath)
        #print(val)
        return str(val[0])

if __name__ == "__main__":
    cfg = Config("NewListingScrapper","DEV")
    cfg.getConfigValue("UserName")
    cfg.getConfigValue("Password")
    cfg.getConfigValue("EntryUrl")