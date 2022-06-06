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

covertDirectionToEng = {'北': 'N', '南': 'S'}



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
        super().readCSVfile()

    def get_equipmentID(self, inputArgs: dict):

        """inputArgs = ['freeway': a, 'direction':b, 'startkilo':c, 'endkilo':d]"""

        directionTransform = {'北': '北向', '南': '南向', '東': '東向', '西': '西向'}

        inputArgs['direction'] = directionTransform[inputArgs['direction']]
        equipmentID = self.CSVFileContent.loc[(self.CSVFileContent['freeway'] == inputArgs['freeway']) &
                                         (self.CSVFileContent['direction'] == inputArgs['direction']) &
                                         (self.CSVFileContent['startkilo'] == inputArgs['endkilo']) &
                                         (self.CSVFileContent['endkilo'] == inputArgs['startkilo'])]['equipmentID']
                                        # 注意: 此處 Startkilo 和 endkilo 設備對照表中 反過來才是正確的
        if equipmentID.empty:
            raise NotFindEquipmentIDError(inputArgs=inputArgs)
        else:
            equipmentID = equipmentID.tolist()[0]  # Convert to String
            return equipmentID

    def get_equipmentName(self, inputArgs: dict):
        """inputArgs = ['freeway': a, 'direction':b, 'startkilo':c, 'endkilo':d]"""

        directionTransform = {'北': '北向', '南': '南向', '東': '東向', '西': '西向'}

        inputArgs['direction'] = directionTransform[inputArgs['direction']]
        stationName = self.CSVFileContent.loc[(self.CSVFileContent['freeway'] == inputArgs['freeway']) &
                                              (self.CSVFileContent['direction'] == inputArgs['direction']) &
                                              (self.CSVFileContent['startkilo'] == inputArgs['endkilo']) &
                                              (self.CSVFileContent['endkilo'] == inputArgs['startkilo'])]['stationName']
        # 注意: 此處 Startkilo 和 endkilo 設備對照表中 反過來才是正確的
        if stationName.empty:
            raise NotFindEquipmentIDError(inputArgs=inputArgs)
        else:
            stationName = stationName.tolist()[0]  # Convert to String
            return stationName


class TrafficVolumeDataParser(CSVParser.CSVParser):

    PCU = {'S': 1.0, 'L': 1.6, 'T': 2.0}

    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute=fileRoute, fileName=fileName)
        self.trafficVolumeDict = {'S': 0, 'L': 0, 'T': 0,
                                  'volume': 0, 'PCU': 0, 'Speed_PCU': 0, 'Speed_volume': 0,
                                  'Var_PCU': 0, 'Var_Speed_PCU': 0, 'Var_Speed_Volume': 0, 'Var_volume': 0}
        self.readCSVfile()

    def get_PCU_Volumes(self):
        PCE = TrafficVolumeDataParser.PCU['S'] * self.trafficVolumeDict['S'] + \
              TrafficVolumeDataParser.PCU['T'] * self.trafficVolumeDict['T'] + \
              TrafficVolumeDataParser.PCU['L'] * self.trafficVolumeDict['L']
        return PCE

    def get_totalTrafficVolumes(self):
        totalVolume = self.trafficVolumeDict['S'] + self.trafficVolumeDict['L'] + self.trafficVolumeDict['T']
        return totalVolume

    def get_trafficVolumes(self, dateTime: datetime, gantryID, direction):
        '''EXAMPLE:
        dateTime = %Y/%m/%d %H:%M
        Direction = 北
        TimeInterval =  2020-02-10 00:00
        trafficVolumeDict = {31: 0, 32: 0, 41: 0, 42: 0, 5: 0}
        '''

        tempResults = {'5': 0, '31': 0, '32': 0, '41': 0, '42': 0}
        directionEng = covertDirectionToEng[direction]
        result = self.CSVFileContent.loc[(self.CSVFileContent['TimeInterval'] == dateTime.strftime("%Y-%m-%d %H:%M")) &
                                         (self.CSVFileContent['GantryID'] == gantryID) &
                                         (self.CSVFileContent['Direction'] == directionEng)]

        if result.empty:
            raise NotFindTrafficVolumeError(inputArgs={'dateTime': datetime, 'gantryID': gantryID, 'direction': direction})

        vehTypeList = result['VehicleType'].tolist()
        trafficList = result['Traffic'].tolist()
        for i in range(5):
            tempResults.update({str(vehTypeList[i]): trafficList[i]})

        self.trafficVolumeDict['S'] = int(tempResults['31']) + int(tempResults['32'])
        self.trafficVolumeDict['L'] = int(tempResults['41']) + int(tempResults['42'])
        self.trafficVolumeDict['T'] = int(tempResults['5'])
        self.trafficVolumeDict['PCU'] = self.get_PCU_Volumes()
        self.trafficVolumeDict['volume'] = self.get_totalTrafficVolumes()

        return self.trafficVolumeDict

class WeatherDataParser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName)
        super().readCSVfile()



if __name__ == '__main__':

    year = '2020'
    freeway = '國道1號'
    direction = '北'

    route = os.path.join('data', year, 'newCombinedCSV', 'addMillionSec') #read: after combined CSV
    csvParser = CSVParser.CSVParser(fileRoute=route, fileName=freeway + '_' + direction + '_new.csv')
    csvParser.readCSVfile(skiprows=[i for i in range(6, 5042500)]
                          ) ##skiprows=[i for i in range(1, 5042300)] ## usecols=['startkilo', 'endkilo', 'year', 'date', 'starttime', 'endtime']

    #csvParser.readCSVfile(method='normal')  # Establish parser object and read csv file


    freewayCSVContentDict[freeway+direction] = csvParser.getCSVfileContent()  # get the content of the csv
    freewayCSVColumnNames = csvParser.getColunmnames()
    print(f"len = {len(freewayCSVContentDict[freeway+direction])}")
    print("save success!")

    MiletoETagGantryConverter = MileToEquipementIDConverter(fileRoute=os.path.join('data', 'MileToGantryReference'),
                                                            fileName='ETC點位對照表_2公里_20220112.csv')
    MiletoWeatherStationConverter = MileToEquipementIDConverter(fileRoute=os.path.join('data', 'MileToGantryReference'),
                                                                fileName='天氣測站對照表_2公里_2019_2020.csv')

    for index, row in freewayCSVContentDict[freeway+direction].iterrows():

        year = row['year']
        date = row['date']
        month = date[0:2]
        day = date[3:]
        starttime = row['starttime']

        startkilo = int(float(row['startkilo']))
        endkilo = int(float(row['endkilo']))

        gantryID = MiletoETagGantryConverter.get_equipmentID(inputArgs={'freeway': freeway, 'direction': direction,
                                                                         'startkilo': startkilo, 'endkilo': endkilo})

        ETCDataRoute = os.path.join('data', 'TrafficVolume', 'M03', str(year), str(int(month))+'月')
        ETCDataName = str(int(day))+'日.csv'
        trafficVolumesParser = TrafficVolumeDataParser(fileRoute=ETCDataRoute, fileName=ETCDataName)
        trafficVolumes = trafficVolumesParser.get_trafficVolumes(dateTime=datetime.strptime(str(year) + '/' + str(date) + " " + str(starttime), '%Y/%m/%d %H:%M'),
                                                   gantryID=gantryID, direction=direction)

        freewayCSVContentDict[freeway+direction].at[index, 'volume_S'] = trafficVolumes['S']
        freewayCSVContentDict[freeway+direction].at[index, 'volume_L'] = trafficVolumes['L']
        freewayCSVContentDict[freeway+direction].at[index, 'volume_T'] = trafficVolumes['T']
        freewayCSVContentDict[freeway+direction].at[index, 'volume'] = trafficVolumes['volume']
        freewayCSVContentDict[freeway+direction].at[index, 'PCU'] = trafficVolumes['PCU']

        stationID = MiletoWeatherStationConverter.get_equipmentID(inputArgs={'freeway': freeway, 'direction': direction,
                                                                              'startkilo': startkilo, 'endkilo': endkilo})
        stationName = MiletoWeatherStationConverter.get_equipmentName(inputArgs={'freeway': freeway, 'direction': direction,
                                                                               'startkilo': startkilo, 'endkilo': endkilo})

        rainDataRoute = os.path.join('data', 'Central Weather Bureau', str(year), 'rain')
        rainDataName = 'Auto_rain_' + str(year-1911) + '_' + stationID
        windDataRoute = os.path.join('data', 'Central Weather Bureau', str(year), 'windspeed')
        windDataName = str(year-1911) + stationName

        ## 0606今天到這邊~~~
        WeatherDataParser(fileRoute=rainDataRoute, fileName=rainDataName)





    freewayCSVContentDict[freeway+direction].to_csv('new1111.csv')


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











