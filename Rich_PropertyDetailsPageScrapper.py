from bs4 import BeautifulSoup
import ast
import XmlConfigReader
import traceback

def parseDetails(sHtml):
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




if __name__ == "__main__":
    f = open("\\testData\\RICHDetail.html", 'r')
    s = f.read()
    parseDetails(s)
