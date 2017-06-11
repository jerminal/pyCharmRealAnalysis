'''
This code scrapps property details using beautiful soup
'''

from bs4 import BeautifulSoup
import ast
import XmlConfigReader
import traceback

#parse a section and returns a dictionary
def parseSection(sectionContent, dictColumns):
    dictResults = {}
    for key in dictColumns:
        try:
            idx = sectionContent.index(dictColumns[key])
            dictResults[key] = sectionContent[idx + 1]
        except:
            #print("{0} not found".format(dictColumns[key]))
            pass
    return dictResults
'''
convert strings led by $ and , to a number
'''
def convertToNumber(entry):
    if entry is None:
        return None
    elif type(entry) is float:
        return entry
    else:
        try:
            return float(entry.strip().replace("$", "").replace(",",""))
        except:
            print("Error occured while trying to convert to float. original value: {0}".format(entry))
            return None

def readAllPropScrapperConfigSections():
    cfg = XmlConfigReader.Config("AllPropScrapper", "DEV")
    # now start retrieve the page section names and column dictionary
    dictSectionLookup = {}
    lstSectKeys = []
    lstSectDict = []
    # general section
    strGeneral = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("General"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("General"))
    dictGeneral = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strGeneral)
    lstSectDict.append(dictGeneral)
    dictSectionLookup[strGeneral] = dictGeneral

    # ListingOffice section
    strListingOffice = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("ListingOffice"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("ListingOffice"))
    dictListingOffice = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strListingOffice)
    lstSectDict.append(dictListingOffice)
    dictSectionLookup[strListingOffice] = dictListingOffice

    # SchoolSection
    strSchool = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("School"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("School"))
    dictSchool = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strSchool)
    lstSectDict.append(dictSchool)
    dictSectionLookup[strSchool] = dictSchool

    # Description section
    strDescription = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Description"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Description"))
    dictDescription = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strDescription)
    lstSectDict.append(dictDescription)
    dictSectionLookup[strDescription] = dictDescription
    # Rooms section
    '''
    strRooms = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Rooms"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Rooms"))
    dictRooms = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strRooms)
    lstSectDict.append(dictRooms)
    '''
    # Additional section
    strAdditional = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Additional"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Additional"))
    dictAdditional = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strAdditional)
    lstSectDict.append(dictAdditional)
    dictSectionLookup[strAdditional] = dictAdditional

    # LeaseAdditinal
    strLeaseAdditional = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("LeaseAdditinal"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("LeaseAdditinal"))
    dictLeaseAdditional = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strLeaseAdditional)
    lstSectDict.append(dictLeaseAdditional)
    dictSectionLookup[strLeaseAdditional] = dictLeaseAdditional

    # Financial section
    strFinancial = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Financial"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Financial"))
    dictFinancial = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strFinancial)
    lstSectDict.append(dictFinancial)
    dictSectionLookup[strFinancial] = dictFinancial

    # Pending section
    strPending = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Pending"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Pending"))
    dictPending = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strPending)
    lstSectDict.append(dictPending)
    dictSectionLookup[strPending] = dictPending

    # Sold section
    strSold = cfg.getConfigValue("PageSections/Section[@name='{0}']/SectionString".format("Sold"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("Sold"))
    dictSold = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strSold)
    lstSectDict.append(dictSold)
    dictSectionLookup[strSold] = dictSold

    # LeasedInformation
    strLeasedInformation = cfg.getConfigValue(
        "PageSections/Section[@name='{0}']/SectionString".format("LeasedInformation"))
    strTemp = cfg.getConfigValue("PageSections/Section[@name='{0}']/ColumnDictionary".format("LeasedInformation"))
    dictLeasedInformation = ast.literal_eval(strTemp.strip())
    lstSectKeys.append(strLeasedInformation)
    lstSectDict.append(dictLeasedInformation)
    dictSectionLookup[strLeasedInformation] = dictLeasedInformation

    return (lstSectKeys, lstSectDict, dictSectionLookup)

def parseDetails(sHtml):
    lstPropTypes = ['Townhouse/Condo','Lots','Multi-Family','Rental','Single-Family']
    (lstSectKeys, lstSectDict, dictSectionLookup ) = readAllPropScrapperConfigSections()

    soup = BeautifulSoup(sHtml, 'lxml')
    #extract all tables' contents
    dataCollect = []
    tables = soup.find_all("table")
    for table in tables:
        for tr in table.findAll('tr'):
            for td in tr.findAll("td"):
                temp = td.find(text=True)
                if temp is None:
                    dataCollect.append(None)
                else:
                    dataCollect.append((temp.replace(u'\xa0', u' ')).strip())
    #print("dataCollect: ")
    #print (dataCollect)
    # now, separate the long string into sections extracted above
    dictSectionContents = {}
    idxStart = 0
    for n, item in enumerate(lstSectKeys):
        if n > 0:
            try:
                idxEnd = dataCollect.index((item).strip())
                dictSectionContents[strKey] = dataCollect[idxStart:idxEnd]
                if n == len(lstSectKeys)-1:
                    #if it's the last in the list of section keys, add that as as well
                    dictSectionContents[item] = dataCollect[idxEnd:]
                idxStart = idxEnd
                strKey = item
            except:
                # item not found, just move on
                #print("section {0} not found".format(item))
                pass
        else:
            strKey = item
    selectedPropType = ''
    for propType in lstPropTypes:
        if propType in dictSectionContents[''][138:142]:
            selectedPropType = propType
    if selectedPropType == '':
        return None

    #now start extract details section by section
    dictResults = {}

    for sectionKey in dictSectionLookup.keys():
        try:
            dictLookup = dictSectionLookup[sectionKey]
            valueList = dictSectionContents[sectionKey]
            for columnKey in dictLookup.keys():
                try:
                    idx = valueList.index(dictLookup[columnKey])
                    columnVal = valueList[idx+1]
                    #print("{0}: {1}".format(columnKey, columnVal))
                except:
                    #print("{0} not found".format(dictLookup[columnKey]))
                    columnVal = None
                dictResults[columnKey] = columnVal
        except:
            print("Section {} doesn't exist in the context".format(sectionKey))
    # now do some clean up
    # BldgSqft: example: 2,705 / Appr Dist, needs to get rid of the part after /
    try:
        entry = dictResults["BldgSqft"]
        if entry is not None:
            dictResults["BldgSqft"] = int((entry.split(' ')[0]).replace(',', ''))
    except KeyError:
        pass
    except:
        print("Exception occured while trying to parse BldgSqft. Original value: {0}".format(entry))
        dictResults["BldgSqft"] = None

    # Days on market: sometimes there is an asterisk after the number

    try:
        entry = dictResults['DaysOnMarket']
        if entry is not None:
            if entry[-1:] == '*':
                dictResults['DaysOnMarket'] = entry[:-1]
    except KeyError:
        pass
    except:
        print("Exception occured while trying to parse DOM. Original value: {0}".format(entry))
        dictResults["DaysOnMarket"] = None
    # lot size:
    try:
        entry = dictResults["LotSize"]
        if entry is not None:
            dictResults["LotSize"] = int((entry.split(' ')[0]).replace(',', ''))
    except KeyError:
        pass
    except:
        print("Exception occured while trying to parse Lotsize. Original value: {0}".format(entry))
        dictResults["LotSize"] = None
    # LPperSqft
    try:
        entry = dictResults['LPperSqft']
        if entry is not None:
            entry = entry[1:]  # pick the number part, leave out the dollar sign
            dictResults['LPperSqft'] = float(entry.replace(',', ''))
    except KeyError:
        pass
    except:
        print("Exception occured while trying to parse LPperSqft. Original value: {0}".format(entry))
        dictResults["LPperSqft"] = None
    # ListPrice
    try:
        entry = dictResults['ListPrice']
        if entry is not None:
            entry = entry[1:]  # pick the number part, leave out the dollar sign
            dictResults['ListPrice'] = float(entry.replace(',', ''))
    except KeyError:
        pass
    except:
        print("Exception occured while trying to parse ListPrice. Original value: {0}".format(entry))
        dictResults["ListPrice"] = None
    # YearBuilt
    try:
        entry = dictResults['YearBuilt']
        if not entry is None:
            dictResults['YearBuilt'] = int(entry.split(' ')[0])
    except KeyError:
        pass
    except:
        print("Exception occured while trying to parse YearBuilt. Original value: {0}".format(entry))
        dictResults["YearBuilt"] = None
    # now separate list agent id and name
    try:
        entry = dictResults['ListAgent']
        if not entry is None:
            dictResults['ListAgentId'] = entry.split('/')[0]
            dictResults['ListAgentName'] = entry.split('/')[1]
    except KeyError:
        pass
    except:
        print("Error occured while trying to generate agent id and name. original value: {0}".format(entry))
        dictResults['ListAgentId'] = entry
        dictResults['ListAgentName'] = entry
    # now separate broker id and name
    try:
        entry = dictResults['ListBroker']
        if not entry is None:
            dictResults['ListBrokerId'] = entry.split('/')[0]
            dictResults['ListBrokerName'] = entry.split('/')[1]
    except KeyError:
        pass
    except:
        print("Error occured while trying to generate broker id and name. original value: {0}".format(entry))
        dictResults['ListBrokerId'] = entry
        dictResults['ListBrokerName'] = entry
    # close agent info
    try:
        entry = dictResults['CloseAgent']
        if not entry is None:
            dictResults['CloseAgentId'] = (entry.split('(')[1]).rstrip(")")
            dictResults['CloseAgentName'] = entry.split('(')[0]
    except KeyError:
        pass
    except:
        print("Error occured while trying to generate close agent id and name. original value: {0}".format(entry))
        dictResults['CloseAgentId'] = entry
        dictResults['CloseAgentName'] = entry
    # sell agent info
    try:
        entry = dictResults['SellAgent']
        if not entry is None:
            dictResults['SellAgentId'] = (entry.split('(')[1]).strip()
            dictResults['SellAgentName'] = (entry.split('(')[0]).rstrip(")")
    except KeyError:
        pass
    except:
        print("Error occured while trying to generate sell agent id and name. original value: {0}".format(entry))
        dictResults['SellAgentId'] = entry
        dictResults['SellAgentName'] = entry
# close broker info
    try:
        entry = dictResults['CloseBroker']
        if not entry is None:
            dictResults['CloseBrokerId'] = (entry.split('(')[1]).rstrip(")")
            dictResults['CloseBrokerName'] = entry.split('(')[0]
    except KeyError:
        pass
    except:
        print("Error occured while trying to generate broker id and name. original value: {0}".format(entry))
        dictResults['CloseBrokerId'] = entry
        dictResults['CloseBrokerName'] = entry

    #onvert dollar to numbers
    try:
        val = dictResults['LeasePrice']
        dictResults['LeasePrice'] = convertToNumber(val)
    except KeyError:
        pass
    except:
        print ("error when processing LeasePrice: {0}".format(traceback.print_exc()))

    #convert application fee to float
    try:
        val = dictResults['ApplicationFee']
        dictResults['ApplicationFee'] = convertToNumber(val)
    except KeyError:
        pass
    except:
        print("error when processing ApplicationFee: {0}".format(traceback.print_exc()))

    # convert Bonue to number
    try:
        val = dictResults['Bonus']
        dictResults['Bonus'] = convertToNumber(val)
    except KeyError:
        pass
    except:
        if val is not None:
            print("error when processing Bonus: {0}".format(traceback.print_exc()))
    try:
        val = dictResults['ApplicationFee']
        dictResults['ApplicationFee'] = convertToNumber(val)
    except KeyError:
        pass
    except:
        print("error when processing ApplicationFee: {0}".format(traceback.print_exc()))

    #LeasedPricePerSqft
    try:
        val = dictResults['LeasedPricePerSqft']
        dictResults['LeasedPricePerSqft'] = convertToNumber(val)
    except KeyError:
        pass
    except:
        print("error when processing LeasePricePerSqft: {0}".format(traceback.print_exc()))

    try:
        val = dictResults['ApplicationFee']
        dictResults['ApplicationFee'] = convertToNumber(val)
    except KeyError:
        pass
    except:
        print("error when processing ApplicationFee: {0}".format(traceback.print_exc()))

    #SalePricePerSqft
    try:
        val = dictResults['SalePricePerSqft']
        dictResults['SalePricePerSqft'] = convertToNumber(val)
    except KeyError:
        pass
    except :
        print("error when processing SalePricePerSqft: {0}".format(traceback.print_exc()))

    # SoldPricePerSqft
    try:
        val = dictResults['SoldPricePerSqft']
        dictResults['SoldPricePerSqft'] = convertToNumber(val)
    except KeyError:
        pass
    except:
        print("error when processing SoldPricePerSqft: {0}".format(traceback.print_exc()))

    dictResults['PropertyType'] = selectedPropType
    return dictResults

#this is unit test code for the module
if __name__ == "__main__":
    #fileName = r'testData/sfh.html'
    fileName = r'testData/th.html'
    s = open(fileName, 'r').read()
    result = parseDetails(s)
    print(result)