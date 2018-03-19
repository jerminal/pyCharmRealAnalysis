#from beautifulsoup4 import  BeautifulSoup
from bs4 import BeautifulSoup
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
    '''
    get a list of the attributes dictionaries under a path
    '''
    def getConfigValues(self, partialPath, bIncludeValue = False):
        xpath = "//data/Application[@name='{0}']/{1}/{2}".format(self._App, self._Inst, partialPath)
        nodes = self._doc.xpath(xpath)
        val = []
        for node in nodes:
            if bIncludeValue:
                print(node.text)
                dict = node.attrib
                dict.update({'Text': node.text})
                val.append(dict)
            else:
                val.append(node.attrib)

        return val

    def getConfigValue(self, partialPath):
        xpath = "//data/Application[@name='{0}']/{1}/{2}/text()".format(self._App, self._Inst, partialPath)
        #print(xpath)
        #val = self._doc.xpath("//data/Application[@name='{0}']/{1}/{2}/text()".format(self._App, self._Inst, partialPath))
        #print(val)
        #xpath = "//Application[@name='{0}']/{1}/{2}/text()".format(self._App, self._Inst, partialPath)
        #print(xpath)
        val = self._doc.xpath(xpath)
        try:
            #retVal = str(val[0]).replace(r'\\', r"\")
            return str(val[0])
        except:
            return ""

if __name__ == "__main__":
    cfg = Config("AllPropScrapper","DEV")
    #cfg.getConfigValue("UserName")
    #cfg.getConfigValue("Password")
    #cfg.getConfigValue("EntryUrl")
    cfg.getConfigValues("PageContents/Section")
    cfg.getConfigValues('PageContents/Section[@name="General"]/Column', True)