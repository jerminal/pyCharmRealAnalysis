import geocoder
import pymysql
import traceback
import datetime
import XmlConfigReader
from censusgeocode import CensusGeocode

cfg = XmlConfigReader.Config("AddrGeocoder", 'DEV')

'''geocode with bing, returns a tuple with the format:
lat, lon, strFullAddr, neighborhood, geocoderName, quality, accuracy, 
'''


def GeoCode(GeoCoder, strAddr):
    strBingMapKey = cfg.getConfigValue(r"Geocoder/BingKey")

    #strBingMapKey = 'AjlU0VglpeaGSVjfdrvFNEEZKSRWLtUYbDGGBbkVq1SsFK6Vz724WpqxqRi2m8SJ'
    try:
        if GeoCoder == 'google':
            g = geocoder.google(strAddr)
            return (g.lat, g.lng, g.address, GeoCoder, g.neighborhood, g.quality, g.accuracy, None)
        elif GeoCoder == 'bing':
            g = geocoder.bing(strAddr, key=strBingMapKey)
            return (g.lat, g.lng, g.address, GeoCoder, g.neighborhood, g.quality, g.accuracy, g.confidence)
        elif GeoCoder == 'census':
            cg = CensusGeocode()
            j = cg.onelineaddress(strAddr)
            try:
                return (j[0]['coordinates']['y'], j[0]['coordinates']['x'], GeoCoder, None, None, None, None, None)
            except:
                return (None, None, GeoCoder, None, None, None, None, None)
        else:
            g = geocoder.yahoo(strAddr)
            return (g.lat, g.lng, g.json['address'], GeoCoder, g.neighborhood, g.quality, g.accuracy, None)

    except:
        print('error encountered when geocoding address: {0}'.format(strAddr))
        traceback.print_exc()
        return (None, None, None, GeoCoder, None, None, None)


'''
    description: it runs through pptid_geo_lkup table and geocode un-geocoded, and badly geocoded items
'''
def runGeoUpdate(geoEngine='google', limit = 2500):
    # first look for entries without any lat/lon
    if geoEngine == 'google':
        sql = "select propertyid, strnum, strname, strdir, strsfx, city, state, zip from pptid_geo_lkup where geolat is null and geolon is null and strnum <> 0 and geogooglemapused is null limit 2500"
    elif geoEngine == 'bing':
        sql = "select propertyid, strnum, strname, strdir, strsfx, city, state, zip from pptid_geo_lkup where geolat is null and geolon is null and strnum <> 0 and geobingmapused is null limit 2500"
    elif geoEngine == 'census':
        sql = "select propertyid, strnum, strname, strdir, strsfx, city, state, zip from pptid_geo_lkup where geolat is null and geolon is null and strnum <> 0 and geocensusmapused is null limit 5000"
    else:
        exit
    host = cfg.getConfigValue(r'MySQL/host')
    port = int(cfg.getConfigValue(r"MySQL/port"))
    user = cfg.getConfigValue(r"MySQL/user")
    passwd = cfg.getConfigValue(r"MySQL/password")
    db = cfg.getConfigValue(r"MySQL/DB")

    cnn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    print('database connected')
    cur = cnn.cursor()
    cur.execute(sql)
    rwsToGeocode = cur.fetchall()
    resultSet = []

    # now prepare to update the record
    if geoEngine == 'google':
        sqlUpdate = "UPDATE pptid_geo_lkup SET geolat=%s, geolon=%s, geoaddress=%s, geogooglemapused=1, geosource=%s, geoneighborhood=%s, geoquality=%s, geoaccuracy=%s, geoconfidence=%s, lastupdate=%s where propertyid=%s"
    elif geoEngine == 'bing':
        sqlUpdate = "UPDATE pptid_geo_lkup SET geolat=%s, geolon=%s, geoaddress=%s, geobingmapused=1, geosource=%s, geoneighborhood=%s, geoquality=%s, geoaccuracy=%s, geoconfidence=%s, lastupdate=%s where propertyid=%s"
    elif geoEngine == 'census':
        sqlUpdate = "UPDATE pptid_geo_lkup SET geolat=%s, geolon=%s, geoaddress=%s, geocensusmapused=1, geosource=%s, geoneighborhood=%s, geoquality=%s, geoaccuracy=%s, geoconfidence=%s, lastupdate=%s where propertyid=%s"
    else:
        sqlUpdate = "UPDATE pptid_geo_lkup SET geolat=%s, geolon=%s, geoaddress=%s, geosource=%s, geoneighborhood=%s, geoquality=%s, geoaccuracy=%s, geoconfidence=%s, lastupdate=%s where propertyid=%s"
    nCnt = 0
    if len(rwsToGeocode) > 0:
        for cnt, row in enumerate(rwsToGeocode):
            idx = row[0]  # property id
            # strAddr = row[1] + " " + row[3] + " " + row[2] + " " + row[4] + ", " + row[5] + " " + row[6] + " " + row[7];
            # example: 123 N Main st, Houston, TX 77701
            strAddr = "{0} {2} {1} {3}, {4}, {5} {6}".format(replaceNone(row[1]), replaceNone(row[2]),
                                                             replaceNone(row[3]), replaceNone(row[4]),
                                                             replaceNone(row[5]),
                                                             replaceNone(row[6]), replaceNone(row[7]))
            print("{0}: address to geocode: {1}".format(cnt, strAddr))
            try:
                rsltGeo = GeoCode(geoEngine, strAddr)
                print("Address geocoded: {0}".format(strAddr))
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item = rsltGeo + (ts, idx)
                #resultSet.append(item)
                try:
                    cur.execute(sqlUpdate, item)

                    print("{0}: property id:{1} updated".format(cnt, item[9]))
                    nCnt += 1
                except:
                    print('error encountered updating property'.format(strAddr))
                    traceback.print_exc()
                if nCnt == 100:
                    cnn.commit()
                    nCnt = 0
            except:
                print('error encountered when geocoding address: {0}'.format(strAddr))
                traceback.print_exc()
    else:
        # now try other geocoding methods
        print('Todo: nothing is implemented yet')


        # then it looks for the ones that are not well geocoded


def run():
    host = cfg.getConfigValue(r'MySQL/host')
    port = int(cfg.getConfigValue(r"MySQL/port"))
    user = cfg.getConfigValue(r"MySQL/user")
    passwd = cfg.getConfigValue(r"MySQL/password")
    db = cfg.getConfigValue(r"MySQL/DB")

    cnn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    print('database connected')
    cur = cnn.cursor()
    print('getting un-geocoded property list...')
    cur.execute(
        "SELECT p.PropertyNumber, p.Situs FROM HARHistory.taxrecord_fortbend_property p inner join (select * from taxrecord_fortbend_geolatlon where GeoGoogleMapUsed is null and GeoLat is null) g on g.PK_PropertyNum = p.PropertyNumber limit 2500")
    print('fetching all records')
    results = cur.fetchall()
    print('records fetched')
    list = []
    cnt = 0
    for row in results:
        if cnt < 1500:
            try:
                propNum = row[0]
                strAddr = row[1]
                print("geocoding {0}".format(strAddr))
                g = geocoder.google(strAddr)
                strGeoAddr = (g.housenumber if g.housenumber is not None else '') + ' ' + (
                g.street if g.street is not None else '') + ', ' + (g.city if g.city is not None else '') + ' ' + (
                             g.state if g.state is not None else '') + ' ' + (g.postal if g.postal is not None else '')
                print(
                    '{0} geocoded. Lat:{1}, Lon:{2}'.format(strGeoAddr, (g.latlng[0] if g.latlng[0] is not None else 0),
                                                            (g.latlng[1] if g.latlng[1] is not None else 0)))
                list.append((row[0], (g.latlng[0] if g.latlng[0] is not None else 0),
                             (g.latlng[1] if g.latlng[1] is not None else 0), strGeoAddr, 'google', 1,
                             datetime.datetime.now()))
            except:
                traceback.print_exc()
                list.append((row[0], None, None, None, 'google', 1, datetime.datetime.now()))

            cnt += 1
    '''
    saveFile = open("c:/temp/geoResults.txt",'w')
    for item in list:
        print(item)
        saveFile.write(','.join( list(map(lambda x:str(x), item)) ))
    saveFile.close()
    '''
    print('starting to update database')
    for row in list:
        try:
            print("inserting {0}".format(row[0]))
            cur.execute(
                "INSERT INTO taxrecord_fortbend_geolatlon (PK_PropertyNum, GeoLat, GeoLon, GeoAddr, GeoSource, GeoGoogleMapUsed, LastUpdate) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                row)
            print('record inserted')

        except:
            traceback.print_exc()
            # input()
            try:
                print('insert failed. updating {0}'.format(row[0]))
                cur.execute(
                    "UPDATE taxrecord_fortbend_geolatlon set GeoLat=%s, GeoLon=%s, GeoAddr=%s, GeoSource=%s, GeoGoogleMapUsed=%s, LastUpdate=%s where PK_PropertyNum=%s",
                    row[1:] + (row[0],))
                print('record updated')

            except:
                print('update failed as well')
                traceback.print_exc()
                # input()
    cnn.commit()
    print('end updating database')


def replaceNone(str):
    if str is None:
        return ''
    else:
        return str


if __name__ == "__main__":
    # main()
    # run()
    runGeoUpdate('google')
    #runGeoUpdate('bing')

    runGeoUpdate('census')
    runGeoUpdate('census')
    runGeoUpdate('census')
    runGeoUpdate('census')
    runGeoUpdate('census')
    runGeoUpdate('census')
    runGeoUpdate('census')
    runGeoUpdate('census')

    # copyFromSqliteToMySql()
