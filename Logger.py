import datetime
def appendToLogFile(nMLS, msg, rawData=None):
    with open("c:\\temp\\realanalysisLog.log", "a") as myfile:
        try:
            myfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + str(nMLS) + '\t' + msg + '\n')
        except:
            myfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + 'Nonetype MLS detected' + '\t' + rawData + '\n')
def dumpToFile(strPath, msg):
    with open(strPath, "a") as myfile:
        myfile.write(msg)
