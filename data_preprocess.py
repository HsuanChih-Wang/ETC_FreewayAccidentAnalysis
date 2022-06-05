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

class NotFindEquipmentIDError(Exception):
    """Exception raised for errors in the input arguments.
      Attributes:
          inputArgs -- input arguments
          message -- explanation of the error
    """
    def __init__(self, inputArgs: dict, message="Can not find equipment ID corresponding to input arguments "):
        self.inputArgs = inputArgs
        self.message = message + str(inputArgs)
        super().__init__(self.message)
    pass

class NotFindTrafficVolumeError(Exception):

    def __init__(self, inputArgs: dict, message="Can not find trafficVolumes "):
        self.inputArgs = inputArgs
        self.message = message + str(inputArgs)
        super().__init__(self.message)
    pass


class MileToEquipementIDConverter(CSVParser.CSVParser):

    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName) #Input: Reference File

    def read_reference_file(self):
        super().readCSVfile(method='dict')

    def get_equipementID(self, inputArgs: dict):
        """inputArgs = ['freeway': a, 'direction':b, 'startkilo':c, 'endkilo':d]"""
        result = 0
        try:
            for row in self.CSVFileContent:
                if row['freeway'] == inputArgs['freeway'] and row['direction'] == inputArgs['direction'] \
                        and row['startkilo'] == inputArgs['startkilo'] and row['endkilo'] == inputArgs['endkilo']:
                    result = row['equipmentID']
            if result == 0:
                raise NotFindEquipmentIDError(inputArgs=inputArgs)
        except NotFindEquipmentIDError:
            print()


class TrafficVolumeDataParser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute=fileRoute, fileName=fileName)
        self.readCSVfile(method='dict')

    def get_trafficVolumes(self, dateTime: datetime, gantryID, direction):
        '''EXAMPLE:
        dateTime = %Y/%m/%d %H:%M
        Direction = 北
        TimeInterval =  2020-02-10 00:00
        trafficVolumeDict = {31: 0, 32: 0, 41: 0, 42: 0, 5: 0}
        '''

        trafficVolumeDict = {'S': 0, 'L': 0, 'T': 0}
        tempResults = {'5': 0, '31': 0, '32': 0, '41': 0, '42': 0}

        for item in self.CSVFileContent:

            if dateTime == datetime.strptime(item['TimeInterval'], '%Y-%m-%d %H:%M') \
                    and gantryID == item['GantryID'] and direction == item['direction']:
                tempResults.update({item['VehicleType']: item['Traffic']})
            if len(tempResults) == 5:
                # trafficVolumeDict collects 5 items means completion
                break

        if len(tempResults) < 5:
            raise NotFindTrafficVolumeError(inputArgs={'dateTime': datetime, 'gantryID': gantryID, 'direction': direction})

        trafficVolumeDict['S'] = int(tempResults['31']) + int(tempResults['32'])
        trafficVolumeDict['L'] = int(tempResults['41']) + int(tempResults['42'])
        trafficVolumeDict['T'] = int(tempResults['5'])

        return trafficVolumeDict



class WeatherDataParser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName)




if __name__ == '__main__':

    route = os.path.join('data', year, 'newCombinedCSV') #read: after combined CSV
    csvParser = CSVParser.CSVParser(fileRoute=route, fileName=freeway + '_' + direction + '_new.csv')
    csvParser.readCSVfile(method='normal')  # Establish parser object and read csv file
    freewayCSVContentDict[freeway+direction] = csvParser.getCSVfileContent()  # get the content of the csv
    freewayCSVColumnNames = csvParser.getColunmnames()
    print(f"len = {len(freewayCSVContentDict[freeway+direction])}")
    print("save success!")

    MiletoETagGantryConverter = MileToEquipementIDConverter(fileRoute='', fileName='ETC點位對照表_2公里_20220112.csv')
    MiletoWeatherStationConverter = MileToEquipementIDConverter(fileRoute='', fileName='天氣測站對照表_2公里_2019_2020.csv')

    for row in freewayCSVContentDict[freeway+direction]:

        year = row[freewayCSVColumnNames.index('year')]
        date = row[freewayCSVColumnNames.index('date')]
        month = date[0:2]
        day = date[3:]
        starttime = row[freewayCSVColumnNames.index('starttime')]

        startkilo = int(float(row[freewayCSVColumnNames.index('startkilo')]))
        endkilo = int(float(row[freewayCSVColumnNames.index('endkilo')]))

        gantryID = MiletoETagGantryConverter.get_equipementID(inputArgs={'freeway':freeway, 'direction':direction,
                                                                         'startkilo':startkilo, 'endkilo': endkilo})

        ETCDataRoute = os.path.join('TrafficVolume', 'M03', str(year), str(int(month))+'月', day+'日')
        ETCDataName = day+'日.csv'
        parser = TrafficVolumeDataParser(fileRoute=ETCDataRoute, fileName=ETCDataName)
        trafficVolumes = parser.get_trafficVolumes(dateTime=datetime.strptime(year + '/' + date + " " + starttime, '%Y/%m/%d %H:%M'),
                                                   gantryID=gantryID, direction=direction)




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

    #fillin_crash_data()

    csvParser.writeCSVfile(method='dict', newFileName=csvParser.fileName + '_addCrash.csv',
                          data=freewayCSVContentDict[freeway+direction])









