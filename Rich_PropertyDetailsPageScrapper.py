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
    dict = {}
    tgAddr = soup.find('span',{"id":"contentBody_lblPropertyAddress"})
    dict['address'] = tgAddr.text

    tgBedsBathStyle = soup.find('span',{"id":"contentBody_lblBedsBathsStyle"})
    dict['bedroom'] = int(tgBedsBathStyle.text.split('/')[0].strip().split(' ')[0])
    dict['bath'] = int(tgBedsBathStyle.text.split('/')[1].strip().split(' ')[0])
    dict['propertytype'] = tgBedsBathStyle.text.split('/')[2].strip()

    tgSaleOrRentAndPrice = soup.find('span', {"id": "contentBody_lblSaleOrRent"})
    dict['transtype'] = tgSaleOrRentAndPrice.text.split(':')[0]
    dict['price'] = float(tgSaleOrRentAndPrice.text.split(' ')[-1].replace('$','').replace(',',''))

    tgListingStatusId = soup.find('span', {"id": "contentBody_lblListingStatusID"})

    tgPropertyDetails = soup.find('div', {"id": "contentBody_divPropertyDetails"})
    #now look for year built:
    lstSubTags = tgPropertyDetails.findChildren()
    for idx, tag in enumerate(lstSubTags):
        if tag.text == 'Year Built:':
            nYearBuilt = int(lstSubTags[idx+1].text)
            dict['yearbuilt'] = nYearBuilt

        if tag.text == 'Finished Sq Ft:':
            nBldgSqft = int(lstSubTags[idx+1].text.replace(',',''))
            dict['bldgsqft'] = nBldgSqft

        if tag.text == 'Property Style:':
            strPropStyle = lstSubTags[idx+1].text
            dict['propertystyle'] = strPropStyle
        if tag.text == 'Monthly HOA:':
            str = lstSubTags[idx+1].text
            dict['monthlyhoa'] = str
        if tag.text == 'Garage:':
            str = lstSubTags[idx+1].text
            dict['garage'] = str

    tgContactInfo = soup.find('div', {"id": "contentBody_divContactInfo"})

    strContactPhone = tgContactInfo.text
    dict['listingcompany'] = strContactPhone.split('Phone ')[0]
    dict['contactphone'] = strContactPhone.split('Phone ')[1]

    return dict


def getPropList(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    tgs = soup.find_all('a')
    lstPropIds = []
    for tg in tgs:
        if tg.has_attr('href'):
            strHref = tg.attrs['href']
            if strHref[:31] == 'PropertyDetails.aspx?ListingID=':
                lstPropIds.append(strHref.split('ListingID=')[1])
    print(lstPropIds)

if __name__ == "__main__":
    '''
    url = "https://www.richclub.org/PropertyDetails.aspx?ListingID=14346"
    r = requests.get(url)
    print( parseDetails(r.text))
    '''
    url = "https://www.richclub.org/PropertyList.aspx?search=searchsfall"
    getPropList(url)