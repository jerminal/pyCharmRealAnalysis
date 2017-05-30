'''
This code scrapps property details using beautiful soup
'''

from bs4 import BeautifulSoup

def parseDetails(sHtml):
    dictGeneralSection = {"MLSNum":"ML#: ", "Status":"Status: ", "ListPrice":"List Price: ", "Address":"Address: ", "Area":"Area: ", "LPperSqft":"LP/SF: ", "TaxID":"Tax Acc #: ", "DaysOnMarket":"DOM: ",
                   "City":"City: ",  "State":"State: ", "County":"County: ", "MasterPlanned":"Master Planned: ", "Location" : "Location:", "MarketArea" : "Market Area:", "Subdivision" : "Subdivision: ",
                   "SectionNum" : "Secction #:", "LotSize" : "Lot Size: ", "BldgSqft" : "SqFt: ", "LotValue" : "Lot Value:", "LeaseAlso" : "Lease Also:", "YearBuilt" : "Year Built: ", "LegalDesc" : "Legal Desc: ", "OrigPrice":"Orig\xa0Price: "}
    #'Listing Office\xa0Information '
    dictListOfficeSection ={"ListBroker" : "List Broker: ", "ListAgent" : "List Agent: ", "BrokerAddress" : "Address: ", "LicensedSupervisor" : "Licensed Supervisor:",
                            "ListAgentId":"ListAgentId: ", "ListAgentName":"ListAgentName:", "ListBrokerId":"ListBrokderId:", "ListBrokerName":"ListBrokerName:"}
    #'School\xa0Information '
    dictSchoolSection = {"SchoolDistrict" : "School District: ", "ElemSchool" : "Elem: ", "MiddleSchool" : "Middle: ", "HighSchool" : "High: "}
    #'Description\xa0Information '
    dictDescSection={"Style" : "Style: ", "Stories" : "# Stories: ", "Type" : "Type: ", "Access":"Access: ", "Acres":"Acres: ", "Bedrooms":"Bedrooms: ", "Baths":"Baths F/H: ","Builder":"Builder Nm: "}
    #'Rooms Information '
    dictRoomsSection = {"Oven":"Oven:", "Roof":"Roof: ", "Flooring":"Flooring: ", "Foundation":"Foundation: ", "Countertops":"Countertops: ", "PrvtPool":"Prvt Pool:",
                   "WaterfrontFeat":"Waterfront Feat: ", "ListDate":"List Date: ", "MaintFee":"Maint. Fee: ", "TaxRate":"Tax Rate: ", "Zip": "Zip Code: ", "AgentEmail":"Agent Email:", "AgentPhone":"Agent Phone: ",
                    "Connections": "Connect: ", "Interior": "Interior: ", "MasterBath": "Master Bath:",
                    "ExteriorCons": "Exterior Constr: ", "Range": "Range:", "LotDesc": "Lot Description: ", "Heating": "Heat: ",
                    "Cooling": "Cool: ", "BedroomsDesc": "Bedrooms: ", }
    #'Interior, Exterior, Utilities and Additional Information '
    dictAddtlSection = {"Oven":"Oven:", "Roof":"Roof: ", "Flooring":"Flooring: ", "Foundation":"Foundation: ", "Countertops":"Countertops: ", "PrvtPool":"Prvt Pool:",
                        "WaterfrontFeat":"Waterfront Feat: ", "ListDate":"List Date: ", "MaintFee":"Maint. Fee: ", "TaxRate":"Tax Rate: ", "Zip": "Zip Code: ", "AgentEmail":"Agent Email:", "AgentPhone":"Agent Phone: ",
                        "Connections": "Connect: ", "Interior": "Interior: ", "MasterBath": "Master Bath:", "ExteriorCons": "Exterior Constr: ", "Range": "Range:", "LotDesc": "Lot Description: ", "Heating": "Heat: ",
                        "Cooling": "Cool: ", "BedroomsDesc": "Bedrooms: ", "PrivatePool":"Prvt Pool: ",  "Heat":"Heat: ", "Restrictions":"Restrictions: ", "TDate":"T/Date: ", "CompSubAgent":"Comp: SubAgt: ",
                        "CompBuyerAgent":"Buyer Agent: ", "Bonus":"Bonus: " }
    #'Financial\xa0Information '
    dictFincSection = {}
    #'Pending\xa0Information '
    dictPendingSection = {"PendingDate":"Pending Date: ","EstCloseDate":"Est Close Dt: ","CloseAgtTRECId":"TREC #: ","CloseAgent":"Sell Agent: ","CloseBroker":"Sell Broker: ","CloseAgentName":"CloseAgentName: ","CloseAgentId":"CloseAgentId: ","CloseBrokerName":"CloseBrokerName: ","CloseBrokerId":"CloseBrokerId:"}
    #'Sold\xa0Information '
    dictSoldSection = {"SalePrice":"Sale Price: ","CloseDate":"Close Date: ","TtlDiscountPts":"Ttl Discount Pts: ","SalePricePerSqft":"SP$/SF: ","DaysToClose":"Days to Close: ","Terms":"Terms: ","NewLoan":"New Loan: ", "InterestRate":"Interest Rate: ", "AmortizeYears":"Amortize Years: "}

    soup = BeautifulSoup(sHtml, 'lxml')
    #extract section 1 details- basic property info
    dataCollect = []
    table = soup.find_all("table", {"class":"d48m17"})
    for tr in table[0].findAll("tr"):
        for td in tr.findAll("td"):
            dataCollect.append(td.find(text=True))
    #extract section 2 details - listing agent information

    tables = soup.find_all("table", {"class": "d48m7"})
    for table in tables:
        for tr in table.findAll("tr"):
            for td in tr.findAll("td"):
                dataCollect.append(td.find(text=True))
    print(dataCollect)



'''
def parsePropertyDetails(sHtml):
    soup = BeautifulSoup(sHtml, 'lxml')
    #extract section 1 details- basic property info
    dataCollect = []
    table = soup.find_all("table", {"class":"d48m17"})
    for tr in table[0].findAll("tr"):
        for td in tr.findAll("td"):
            dataCollect.append(td.find(text=True))
    #extract section 2 details - listing agent information

    tables = soup.find_all("table", {"class": "d48m7"})
    for table in tables:
        for tr in table.findAll("tr"):
            for td in tr.findAll("td"):
                dataCollect.append(td.find(text=True))
    print(dataCollect)
    dictColumns = {"MLSNum":"ML#: ", "Status":"Status: ", "ListPrice":"List Price: ", "Address":"Address: ", "Area":"Area: ", "LPperSqft":"LP/SF: ", "TaxID":"Tax Acc #: ", "DaysOnMarket":"DOM: ",
                   "City":"City: ",  "State":"State: ", "County":"County: ", "MasterPlanned":"Master Planned: ", "Location" : "Location:", "MarketArea" : "Market Area:", "Subdivision" : "Subdivision: ",
                   "SectionNum" : "Secction #:", "LotSize" : "Lot Size: ", "BldgSqft" : "SqFt: ", "LotValue" : "Lot Value:", "LeaseAlso" : "Lease Also:", "YearBuilt" : "Year Built: ", "LegalDesc" : "Legal Desc: ",
                   "ListBroker" : "List Broker: ", "ListAgent" : "List Agent: ", "BrokerAddress" : "Address: ", "LicensedSupervisor" : "Licensed Supervisor:", "SchoolDistrict" : "School District: ", "ElemSchool" : "Elem: ",
                   "MiddleSchool" : "Middle: ", "HighSchool" : "High: ", "Style" : "Style: ", "Stories" : "# Stories: ", "Type" : "Type: ", "Access":"Access: ", "Acres":"Acres: ", "Bedrooms":"Bedrooms: ", "Baths":"Baths F/H: ",
                   "Builder":"Builder Nm: ", "Oven":"Oven:", "Roof":"Roof: ", "Flooring":"Flooring: ", "Foundation":"Foundation: ", "Countertops":"Countertops: ", "PrvtPool":"Prvt Pool:",
                   "WaterfrontFeat":"Waterfront Feat: ", "ListDate":"List Date: ", "MaintFee":"Maint. Fee: ", "TaxRate":"Tax Rate: ", "Zip": "Zip Code: ", "AgentEmail":"Agent Email:", "AgentPhone":"Agent Phone: ",
                    "Connections": "Connect: ", "Interior": "Interior: ", "MasterBath": "Master Bath:",
                    "ExteriorCons": "Exterior Constr: ", "Range": "Range:", "LotDesc": "Lot Description: ", "Heating": "Heat: ",
                    "Cooling": "Cool: ", "BedroomsDesc": "Bedrooms: ", "ListAgentId":"ListAgentId: ", "ListAgentName":"ListAgentName:", "ListBrokerId":"ListBrokderId:", "ListBrokerName":"ListBrokerName:",
                   "SellAgentTRECId": "TREC #: ", "SalePrice":"Sale Price: ", "CloseDate": "Close Date: ", "SalePricePerSqft": "SP$/SF: ", "DaysToClose": "Days to Close: ", "FinTerms": "Terms:", "AmortizeYears": "Amortize Years: ",
                    "NewLoan": "New Loan: ", "PendingDate": "Pending Date: ", "EstCloseDate": "Est Close Dt: ", "CoOp":"CoOp: "
    }
    dictResults = {}
    for key in dictColumns:
        try:
            idx = dataCollect.index(dictColumns[key])
            dictResults[key] = dataCollect[idx+1]
        except:
            print ("{0} not found".format(dictColumns[key]))
    print (dictResults)
    #now do some clean up
    #BldgSqft: example: 2,705 / Appr Dist, needs to get rid of the part after /
    try:
        entry = dictResults["BldgSqft"]
        dictResults["BldgSqft"] = int((entry.split(' ')[0]).replace(',',''))
    except:
        print ("Exception occured while trying to parse BldgSqft. Original value: {0}".format(entry))
        dictResults["BldgSqft"] = None

    #Days on market: sometimes there is an asterisk after the number

    try:
        entry = dictResults['DaysOnMarket']
        if entry[-1:] == '*':
            dictResults['DaysOnMarket'] = entry[:-1]
    except:
        print("Exception occured while trying to parse DOM. Original value: {0}".format(entry))
        dictResults["DaysOnMarket"] = None
    #lot size:
    try:
        entry = dictResults["LotSize"]
        dictResults["LotSize"] = int((entry.split(' ')[0]).replace(',',''))
    except:
        print("Exception occured while trying to parse Lotsize. Original value: {0}".format(entry))
        dictResults["LotSize"] = None
    #LPperSqft
    try:
        entry = dictResults['LPperSqft'][1:] # pick the number part, leave out the dollar sign
        dictResults['LPperSqft'] = float(entry.replace(',',''))
    except:
        print("Exception occured while trying to parse LPperSqft. Original value: {0}".format(entry))
        dictResults["LPperSqft"] = None
    #ListPrice
    try:
        entry = dictResults['ListPrice'][1:]  # pick the number part, leave out the dollar sign
        dictResults['ListPrice'] = float(entry.replace(',', ''))
    except:
        print("Exception occured while trying to parse ListPrice. Original value: {0}".format(entry))
        dictResults["ListPrice"] = None
    #YearBuilt
    try:
        entry = dictResults['YearBuilt']
        dictResults['YearBuilt'] = int(entry.split(' ')[0])
    except:
        print("Exception occured while trying to parse YearBuilt. Original value: {0}".format(entry))
        dictResults["YearBuilt"] = None
    #now separate list agent id and name
    try:
        entry = dictResults['ListAgent']
        dictResults['ListAgentId'] = entry.split('/')[0]
        dictResults['ListAgentName'] = entry.split('/')[1]
    except:
        print("Error occured while trying to generate agent id and name. original value: {0}".format(entry))
        dictResults['ListAgentId'] = entry
        dictResults['ListAgentName'] = entry
    #now separate broker id and name
    try:
        entry = dictResults['ListBroker']
        dictResults['ListBrokerId'] = entry.split('/')[0]
        dictResults['ListBrokerName'] = entry.split('/')[1]
    except:
        print("Error occured while trying to generate broker id and name. original value: {0}".format(entry))
        dictResults['ListBrokerId'] = entry
        dictResults['ListBrokerName'] = entry
    return dictResults
'''

#this is unit test code for the module
if __name__ == "__main__":
    fileName = r'c:/temp/AllPropSold_0.html'
    s = open(fileName, 'r').read()
    result = parseDetails(s)
    print(result)