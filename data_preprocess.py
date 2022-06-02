import csv
import os
import CSVParser
from datetime import datetime, timedelta
import mysql.connector
import bisect

Freeway_info={'國道1號': ['北向', '南向'],
              '國道1號高架': ['北向', '南向'],
              '國道2號': ['西向', '東向'],
              '國道3號': ['北向', '南向'],
              '國道3甲號': ['西向', '東向'],
              '國道5號': ['北向', '南向']}

freewayMaxMiles = {'國道1號': 100, '國道2號': 0, '國道3號': 110, '國道3甲號': 0, '國道5號': 0}

freewayCSVContentDict = {'國道1號北': 0, '國道1號南': 0, '國道3號北': 0, '國道3號南': 0}

year = '2020'
freeway = '國道1號'
direction = '北'


class MysqlConnector():

    def __init__(self, host, user, password, database):
        self.host = host
        self.port = 0
        self.user = user
        self.password = password
        self.database = database
        self.dbConnect = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def executeSQLCommand(self, sql: str):
        # preparing a cursor object
        cursorObject = self.dbConnect.cursor()
        cursorObject.execute(sql)

    def closeConnect(self):
        self.dbConnect.close()

class ETC_Data_Parser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName, ETC_GateReferenceFileName):
        super().__init__(fileRoute=fileRoute, fileName=fileName)
        self.ETC_GateReferenceFileName = ETC_GateReferenceFileName

    #里程轉換成ETC和VD的ID
    def mile2ID(self):

        #ETC_ID對照表 [就參考這個ETC]
        ETC_mile2ID = {}
        referenceFile=os.path.join(os.getcwd(), self.fileRoute, self.ETC_GateReferenceFileName)
        f = open(referenceFile, 'r', newline='')
        reader = csv.reader(f)
        for line in reader:
            name = line[0]+line[1]+'_'+str(min(float(line[2]), float(line[3])))
            ETC_mile2ID[name] = line[4]

        f.close()

        return ETC_mile2ID


class Weather_Data_Parser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName)

class Crash_Data_Parser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName)

    def find_paired_crash_data(self):
        return 0

    def writeCSVfile(self, method:str, newFileName:str, data):
        print("123")


if __name__ == '__main__':

    route = os.path.join('data', year, 'newCombinedCSV') #read: after combined CSV
    csvParser = CSVParser.CSVParser(fileRoute=route, fileName=freeway + '_' + direction + '_new.csv')
    csvParser.readCSVfile(method='normal')  # Establish parser object and read csv file
    freewayCSVContentDict[freeway+direction] = csvParser.getCSVfileContent()  # get the content of the csv
    freewayCSVColumnNames = csvParser.getColunmnames()
    print(f"len = {len(freewayCSVContentDict[freeway+direction])}")
    print("save success!")


    #ETC_Data_Parser(fileRoute=route, fileName=free)









    #mysqlConnector = MysqlConnector(host='localhost', user='root', password='wang71026', database='freeway')

    # def fillin_crash_data():
    #     crashFileNames = ['109_國道1號北_已排序.csv']
    #     crashIndexList = []
    #     forLoopBgnIndex = 0
    #
    #     for fileName in crashFileNames:
    #         crashFileParser = Crash_Data_Parser(fileRoute=os.path.join('data', '事故處理資料'), fileName=fileName)
    #         crashFileParser.readCSVfile(method='normal')  # read csv file
    #         crashContent = crashFileParser.getCSVfileContent()  #get the content of the csv
    #         crashColumnNames = crashFileParser.getColunmnames()  #get column names of the csv file
    #
    #         for crashData in crashContent:  # iterate each crash record
    #             crashDateAndTime = datetime.strptime(crashData[crashColumnNames.index('發生日期')] + ' ' + crashData[crashColumnNames.index('時')] + ':'
    #                                                  + crashData[crashColumnNames.index('分')], '%Y-%m-%d %H:%M')
    #
    #             crashDateAndTime_MillionSec = crashDateAndTime.timestamp()
    #             freewayNumber = crashData[crashColumnNames.index('道路')]
    #             dir = crashData[crashColumnNames.index('方向')]
    #             crashMile = int(crashData[crashColumnNames.index('發生公里')])
    #
    #             print("find data!")
    #
    #
    #             for item in freewayCSVContentDict[freeway+direction]:
    #
    #                 year = item[freewayCSVColumnNames.index('year')]
    #                 date = item[freewayCSVColumnNames.index('date')]
    #                 starttime = item[freewayCSVColumnNames.index('starttime')]
    #                 endtime = item[freewayCSVColumnNames.index('endtime')]
    #                 startkilo = int(float(item[freewayCSVColumnNames.index('startkilo')]))
    #                 endkilo = int(float(item[freewayCSVColumnNames.index('endkilo')]))
    #                 crashStartTime = datetime.strptime(year + '/' + date + " " + starttime, '%Y/%m/%d %H:%M')
    #                 crashEndTime = datetime.strptime(year + '/' + date + " " + endtime, '%Y/%m/%d %H:%M')
    #
    #
    #     #print(crashIndexList)
    #     return 0
    #
    # fillin_crash_data()
    #
    # csvParser.writeCSVfile(method='dict', newFileName=csvParser.fileName + '_addCrash.csv',
    #                       data=freewayCSVContentDict[freeway+direction])









