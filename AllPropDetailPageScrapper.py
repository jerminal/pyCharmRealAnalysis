'''
This code scrapps property details using beautiful soup
'''

from bs4 import BeautifulSoup
import ast
import XmlConfigReader

#parse a section and returns a dictionary
def parseSection(sectionContent, dictColumns):
    dictResults = {}
    for key in dictColumns:
        try:
            idx = sectionContent.index(dictColumns[key])
            dictResults[key] = sectionContent[idx + 1]
        except:
            print("{0} not found".format(dictColumns[key]))
    return dictResults


def parseDetails(sHtml):
    cfg = XmlConfigReader.Config("AllPropScrapper","DEV")
    #now start retrieve the page section names and column dictionary
    lstSectKeys = []
    lstSectDict = []
    #general section
    strGeneral = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("General"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("General"))
    dictGeneral = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strGeneral)
    lstSectDict.append(dictGeneral)

    #ListingOffice section
    strListingOffice = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("ListingOffice"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("ListingOffice"))
    dictListingOffice = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strListingOffice)
    lstSectDict.append(dictListingOffice)
    #SchoolSection
    strSchool = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("School"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("School"))
    dictSchool = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strSchool)
    lstSectDict.append(dictSchool)

    #Description section
    strDescription = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Description"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Description"))
    dictDescription = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strDescription)
    lstSectDict.append(dictDescription)
    #Rooms section
    '''
    strRooms = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Rooms"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Rooms"))
    dictRooms = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strRooms)
    lstSectDict.append(dictRooms)
    '''
    #Additional section
    strAdditional = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Additional"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Additional"))
    dictAdditional = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strAdditional)
    lstSectDict.append(dictAdditional)

    #Financial section
    strFinancial = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Financial"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Financial"))
    dictFinancial = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strFinancial)
    lstSectDict.append(dictFinancial)
    # Pending section
    strPending = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Pending"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Pending"))
    dictPending = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strPending)
    lstSectDict.append(dictPending)
    # Sold section
    strSold = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Sold"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Sold"))
    dictSold = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strSold)
    lstSectDict.append(dictSold )

    soup = BeautifulSoup(sHtml, 'lxml')
    #extract section 1 details- basic property info
    dataCollect = []
    table = soup.find_all("table", {"class":"d82m7"})
    for tr in table[0].findAll("tr"):
        for td in tr.findAll("td"):
            temp = td.find(text=True)
            if temp is None:
                dataCollect.append(None)
            else:
                dataCollect.append(temp.replace(u'\xa0', u' '))
    #extract section 2 details - listing agent information
    tables = soup.find_all("table", {"class": "d48m7"})
    for table in tables:
        for tr in table.findAll("tr"):
            for td in tr.findAll("td"):
                temp = td.find(text=True)
                if temp is None:
                    dataCollect.append(None)
                else:
                    dataCollect.append(temp.replace(u'\xa0', u' '))
    print(dataCollect)
    #now, separate the long string into sections extracted above
    sections = []
    idxStart = 0
    for n, item in enumerate(lstSectKeys):
        if n>0:
            idxEnd = dataCollect.index(item)
            sections.append(dataCollect[idxStart:idxEnd])
            idxStart = idxEnd
    print(sections)
    dictResults = {}
    for n, section in enumerate(sections):
        dictResults.update(parseSection(section, lstSectDict[n]))

    print(dictResults)
    # now do some clean up
    # BldgSqft: example: 2,705 / Appr Dist, needs to get rid of the part after /
    try:
        entry = dictResults["BldgSqft"]
        dictResults["BldgSqft"] = int((entry.split(' ')[0]).replace(',', ''))
    except:
        print("Exception occured while trying to parse BldgSqft. Original value: {0}".format(entry))
        dictResults["BldgSqft"] = None

    # Days on market: sometimes there is an asterisk after the number

    try:
        entry = dictResults['DaysOnMarket']
        if entry[-1:] == '*':
            dictResults['DaysOnMarket'] = entry[:-1]
    except:
        print("Exception occured while trying to parse DOM. Original value: {0}".format(entry))
        dictResults["DaysOnMarket"] = None
    # lot size:
    try:
        entry = dictResults["LotSize"]
        dictResults["LotSize"] = int((entry.split(' ')[0]).replace(',', ''))
    except:
        print("Exception occured while trying to parse Lotsize. Original value: {0}".format(entry))
        dictResults["LotSize"] = None
    # LPperSqft
    try:
        entry = dictResults['LPperSqft'][1:]  # pick the number part, leave out the dollar sign
        dictResults['LPperSqft'] = float(entry.replace(',', ''))
    except:
        print("Exception occured while trying to parse LPperSqft. Original value: {0}".format(entry))
        dictResults["LPperSqft"] = None
    # ListPrice
    try:
        entry = dictResults['ListPrice'][1:]  # pick the number part, leave out the dollar sign
        dictResults['ListPrice'] = float(entry.replace(',', ''))
    except:
        print("Exception occured while trying to parse ListPrice. Original value: {0}".format(entry))
        dictResults["ListPrice"] = None
    # YearBuilt
    try:
        entry = dictResults['YearBuilt']
        dictResults['YearBuilt'] = int(entry.split(' ')[0])
    except:
        print("Exception occured while trying to parse YearBuilt. Original value: {0}".format(entry))
        dictResults["YearBuilt"] = None
    # now separate list agent id and name
    try:
        entry = dictResults['ListAgent']
        dictResults['ListAgentId'] = entry.split('/')[0]
        dictResults['ListAgentName'] = entry.split('/')[1]
    except:
        print("Error occured while trying to generate agent id and name. original value: {0}".format(entry))
        dictResults['ListAgentId'] = entry
        dictResults['ListAgentName'] = entry
    # now separate broker id and name
    try:
        entry = dictResults['ListBroker']
        dictResults['ListBrokerId'] = entry.split('/')[0]
        dictResults['ListBrokerName'] = entry.split('/')[1]
    except:
        print("Error occured while trying to generate broker id and name. original value: {0}".format(entry))
        dictResults['ListBrokerId'] = entry
        dictResults['ListBrokerName'] = entry
    return dictResults

#this is unit test code for the module
if __name__ == "__main__":
    fileName = r'c:/temp/AllPropSold_0.html'
    s = open(fileName, 'r').read()
    result = parseDetails(s)
    print(result)