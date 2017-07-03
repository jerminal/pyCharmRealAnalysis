import datetime
def appendToLogFile(nMLS, msg):
    with open("c:\\temp\\realanalysisLog.log", "a") as myfile:
        myfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + str(nMLS) + '\t' + msg + '\n')
