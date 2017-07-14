from bs4 import BeautifulSoup
import requests
import ast
import XmlConfigReader
import traceback

def parseDetails(sHtml):
    '''
    #single
    xpPropertyType = "/html[@class='whatinput-types-initial whatinput-types-mouse']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-8 large-8 columns']/article/div[@class='row']/div[@class='small-12 medium-6 large-6 columns'][2]/h4[1]/span[@id='contentBody_lblBedsBathsStyle']"
    #multi
    xpPropertyType = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-8 large-8 columns']/article/div[@class='row']/div[@class='small-12 medium-6 large-6 columns'][2]/h4[1]/span[@id='contentBody_lblBedsBathsStyle']"
    #comm
    xpPropertyType = "/html[@class='whatinput-types-initial whatinput-types-mouse']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-8 large-8 columns']/article/div[@class='row']/div[@class='small-12 medium-6 large-6 columns'][2]/h4[1]/span[@id='contentBody_lblBedsBathsStyle']"
    xpAddr = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row column'][1]/h3[@class='text-center']/span[@id='contentBody_lblPropertyAddress']"
    xpPrice = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-8 large-8 columns']/article/div[@class='row']/div[@class='small-12 medium-6 large-6 columns'][2]/p[1]/span[@id='contentBody_lblSaleOrRent']"
    xpStatus = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-8 large-8 columns']/article/div[@class='row']/div[@class='small-12 medium-6 large-6 columns'][2]/h4[2]/span[@id='contentBody_lblListingStatusID']"
    xpPropertyStyle = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-4 large-4 columns']/aside/div[@id='contentBody_divPropertyDetails']/div[@class='column text-center'][1]/p/small"
    xpYearBuilt = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-4 large-4 columns']/aside/div[@id='contentBody_divPropertyDetails']/div[@class='column text-center'][2]/p/small"
    xpSqft = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-4 large-4 columns']/aside/div[@id='contentBody_divPropertyDetails']/div[@class='column text-center'][3]/p/small"
    xpCompanyAndPhone = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-8 large-8 columns']/article/div[@class='row']/div[@class='small-12 medium-6 large-6 columns'][2]/div[@id='contentBody_divContactInfo']/span"
    xpWebsite = "/html[@class='whatinput-types-initial whatinput-types-mouse whatinput-types-keyboard']/body/form[@id='form1']/div[@class='body-wrap']/section[@class='properties']/div[@id='contentBody_panelData']/div[@class='row']/div[@class='small-12 medium-8 large-8 columns']/article/div[@class='row']/div[@class='small-12 medium-6 large-6 columns'][2]/p[3]/a[@id='contentBody_lnkMoreInfo']"
    '''
    soup = BeautifulSoup(sHtml)
    tgAddr = soup.find('span',{"id":"contentBody_lblPropertyAddress"})
    print(tgAddr.text)
    tgBedsBathStyle = soup.find('span',{"id":"contentBody_lblBedsBathsStyle"})
    tgSaleOrRentAndPrice = soup.find('span', {"id": "contentBody_lblSaleOrRent"})
    tgListingStatusId = soup.find('span', {"id": "contenBody_lblListingStatusID"})

    tgPropertyDetails = soup.find('div', {"id": "contentBody_divPropertyDetails"})

    tgContactInfo = soup.find('div', {"id": "contentBody_divContactInfo"})
    strContactPhone = tgContactInfo.text


if __name__ == "__main__":
    url = "https://www.richclub.org/PropertyDetails.aspx?ListingID=14346"
    r = requests.get(url)
    parseDetails(r.text)
