import csv
import os
import CSVParser
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, timedelta
import mysql.connector

Freeway_info={'國道1號': ['北向', '南向'],
              '國道1號高架': ['北向', '南向'],
              '國道2號': ['西向', '東向'],
              '國道3號': ['北向', '南向'],
              '國道3甲號': ['西向', '東向'],
              '國道5號': ['北向', '南向']}

freewayMaxMiles = {'國道1號': 100, '國道2號': 0, '國道3號': 110, '國道3甲號': 0, '國道5號': 0}

freewayCSVContentDict = {'國道1號北': 0, '國道1號南': 0, '國道3號北': 0, '國道3號南': 0}

covertDirectionToEng = {'北': 'N', '南': 'S'}

rainDataParserDict = {}
rainStationIDList = np.array(['C0A53', 'C0A54', 'C0ACA', 'C0AD5', 'C0AH0', 'C0AH1',
                    'C0C54', 'C0C62', 'C0C65', 'C0D48', 'C0D56', 'C0D57',
                    'C0D65', 'C0U78', 'C0U99'])

windDataParserDict = {}
windStationIDList = np.array(['五結', '員山', '四堵', '坪林', '大園',
                     '平鎮', '打鐵坑', '新莊', '永和', '汐止',
                     '湖口', '竹東', '蘆竹', '香山', '鶯歌'])

etagDataParserDict = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {},
                      7: {}, 8: {}, 9: {}, 10: {}, 11: {}, 12: {}}

# etagMonthList = np.array(['1月', '2月', '3月', '4月', '5月', '6月'
#                           '7月', '8月', '9月', '10月', '11月', '12月'])


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

class NotFindWindSpeedError(Exception):
    def __init__(self, inputArgs, message="Can not find Windspeed, the input datetime is = "):
        self.inputArgs = inputArgs
        self.message = message + inputArgs
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
        # equipmentID = self.CSVFileContent.at[(self.CSVFileContent['freeway'] == inputArgs['freeway']) &
        #                                  (self.CSVFileContent['direction'] == inputArgs['direction']) &
        #                                  (self.CSVFileContent['startkilo'] == inputArgs['endkilo']) &
        #                                  (self.CSVFileContent['endkilo'] == inputArgs['startkilo'])]['equipmentID']

        c1 = (self.CSVFileContent.freeway == inputArgs['freeway'])
        c2 = (self.CSVFileContent.direction == inputArgs['direction'])
        c3 = (self.CSVFileContent.startkilo == inputArgs['endkilo'])
        c4 = (self.CSVFileContent.endkilo == inputArgs['startkilo'])
        # 注意: 此處 Startkilo 和 endkilo 設備對照表中 反過來才是正確的

        index = (c1 & c2 & c3 & c4).idxmax()
        equipmentID = self.CSVFileContent.at[index, 'equipmentID']

        if equipmentID:
            return equipmentID
        else:
            raise NotFindEquipmentIDError(inputArgs=inputArgs)

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

    def __get_trafficVolumes(self, dateTime: datetime, gantryID, direction):
        '''EXAMPLE:
        dateTime = %Y/%m/%d %H:%M
        Direction = 北
        TimeInterval =  2020-02-10 00:00
        trafficVolumeDict = {31: 0, 32: 0, 41: 0, 42: 0, 5: 0}
        '''

        tempResults = {'5': 0, '31': 0, '32': 0, '41': 0, '42': 0}
        directionEng = covertDirectionToEng[direction]

        c1 = (self.CSVFileContent['TimeInterval'] == dateTime.strftime("%Y-%m-%d %H:%M"))
        c2 = (self.CSVFileContent['GantryID'] == gantryID)
        c3 = (self.CSVFileContent['Direction'] == directionEng)
        result = self.CSVFileContent.loc[c1 & c2 & c3]

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

    def get_trafficVolumes(self, dateTime: datetime, gantryID, direction):
        tempResults = {'5': 0, '31': 0, '32': 0, '41': 0, '42': 0}
        directionEng = covertDirectionToEng[direction]

        c1 = (self.CSVFileContent['TimeInterval'] == dateTime.strftime("%Y-%m-%d %H:%M"))
        c2 = (self.CSVFileContent['GantryID'] == gantryID)
        c3 = (self.CSVFileContent['Direction'] == directionEng)
        indexList = self.CSVFileContent.index[(c1 & c2 & c3)].tolist()

        if not indexList:
            raise NotFindTrafficVolumeError(inputArgs={'dateTime': datetime, 'gantryID': gantryID, 'direction': direction})

        vehTypeList = []
        trafficList = []
        for index in indexList:
            vehTypeList.append(self.CSVFileContent.at[index, 'VehicleType'])
            trafficList.append(self.CSVFileContent.at[index, 'Traffic'])
        for i in np.arange(5):
            tempResults.update({str(vehTypeList[i]): trafficList[i]})
        self.trafficVolumeDict['S'] = int(tempResults['31']) + int(tempResults['32'])
        self.trafficVolumeDict['L'] = int(tempResults['41']) + int(tempResults['42'])
        self.trafficVolumeDict['T'] = int(tempResults['5'])
        self.trafficVolumeDict['PCU'] = self.get_PCU_Volumes()
        self.trafficVolumeDict['volume'] = self.get_totalTrafficVolumes()

        return self.trafficVolumeDict

class RainDataParser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName)

    def get_rainfall(self, startTime: datetime, endTime: datetime):
        condition1 = (pd.to_datetime(self.CSVFileContent['DTIME']) >= startTime)
        condition2 = (pd.to_datetime(self.CSVFileContent['DTIME']) <= endTime)
        indexList = self.CSVFileContent.index[(condition1 & condition2)].tolist()
        if not indexList:
            rainfall = 0.0
            return rainfall
        rainfallList = []
        for index in indexList:
            rainfallList.append(self.CSVFileContent.at[index, 'RN'])

        rainfall = np.sum(rainfallList)

        return rainfall

class WindDataParser(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName)

    def get_windspeed(self, endtime: datetime):
        self.CSVFileContent['時間'] = self.CSVFileContent['時間'].replace(['24:00:00'], '00:00') #一個坑

        index = (pd.to_datetime('20' + self.CSVFileContent['日期'] + " " + self.CSVFileContent['時間']) >= endtime).idxmax()
        #挑出 >= endTime 最接近的那一個時間點
        # if not index:
        #     raise NotFindWindSpeedError(inputArgs=endtime.strftime('%Y/%m/%d %H:%M'))
        # else:
        windspeed = self.CSVFileContent.at[index, '風速']
        return windspeed


if __name__ == '__main__':

    YEAR = '2020'
    FREEWAY = '國道1號'
    direction = '北'
    DOWN_LIMIT = 5042319
    UPPER_LIMIT = 5042300
    MONTH = 12

    def store_rainCSVData():
        rainDataRoute = os.path.join('data', 'Central Weather Bureau', str(YEAR), 'rain')
        for rainStationID in rainStationIDList:
            rainDataName = 'Auto_rain_' + str(int(YEAR)-1911) + '_' + rainStationID + '.csv'
            rainDataParser = RainDataParser(fileRoute=rainDataRoute, fileName=rainDataName)
            rainDataParser.readCSVfile(usecols=['DTIME', 'RN'])  #只挑兩個有用到的欄位
            rainDataParserDict.update({rainStationID: rainDataParser})
        print("Load RAIN CSV DATA DONE!")
        return 0

    def store_windCSVData():
        windDataRoute = os.path.join('data', 'Central Weather Bureau', str(YEAR), 'windspeed')
        for windStationID in windStationIDList:
            windDataName = str(int(YEAR)-1911) + windStationID + '.csv'
            windspeedDataParser = WindDataParser(fileRoute=windDataRoute, fileName=windDataName)
            windspeedDataParser.readCSVfile(usecols=['日期', '時間', '風速', '風向'])
            windDataParserDict.update({windStationID: windspeedDataParser})
        print("Load WIND CSV DATA DONE!")
        return 0

    def store_etagCSVData(year):
        for month in np.arange(1, MONTH + 1):
            numberOfDays = calendar.monthrange(int(YEAR), month)[1]
            for day in np.arange(1, numberOfDays + 1):
                MonthInString = str(int(month))+'月'
                ETCDataRoute = os.path.join('data', 'TrafficVolume', 'M03', str(year), MonthInString)
                ETCDataName = str(int(day))+'日.csv'
                trafficVolumeDataParser = TrafficVolumeDataParser(fileRoute=ETCDataRoute, fileName=ETCDataName)
                etagDataParserDict[month].update({day: trafficVolumeDataParser})
        print("Load ETAG DATA DONE!")
        return 0


    route = os.path.join('data', YEAR, 'newCombinedCSV', 'addMillionSec') #read: after combined CSV
    csvParser = CSVParser.CSVParser(fileRoute=route, fileName=FREEWAY + '_' + direction + '_new.csv')
    csvParser.readCSVfile(skiprows=[i for i in np.arange(DOWN_LIMIT, UPPER_LIMIT)]) ##skiprows=[i for i in range(1, 5042300)] ## usecols=['startkilo', 'endkilo', 'year', 'date', 'starttime', 'endtime']

    freewayCSVContentDict[FREEWAY+direction] = csvParser.getCSVfileContent()  # get the content of the csv
    freewayCSVColumnNames = csvParser.getColunmnames()
    print(f"len = {len(freewayCSVContentDict[FREEWAY+direction])}")
    print("save success!")

    MiletoETagGantryConverter = MileToEquipementIDConverter(fileRoute=os.path.join('data', 'MileToGantryReference'),
                                                            fileName='ETC點位對照表_2公里_20220112.csv')
    MiletoWeatherStationConverter = MileToEquipementIDConverter(fileRoute=os.path.join('data', 'MileToGantryReference'),
                                                                fileName='天氣測站對照表_2公里_2019_2020.csv')
    store_rainCSVData()  #儲存雨量測站表
    store_windCSVData()  #儲存風向測站表
    store_etagCSVData(year=YEAR) #儲存etag資料


    def new_start(df):
        year = df['year']
        date = df['date']
        month = date[0:2]
        day = date[3:]
        starttime = df['starttime']
        endtime = df['endtime']
        starttimeDTform = pd.to_datetime(str(year) + '/' + str(date) + " " + str(starttime), '%Y/%m/%d %H:%M')
        endtimeDTform = pd.to_datetime(str(year) + '/' + str(date) + " " + str(endtime), '%Y/%m/%d %H:%M')

        return 0


    def start(row):
        index = row['index']
        print(f'index = {index}')

        # decompose data
        year = row['year'] #year
        date = row['date'] #date
        month = date[0:2] #month
        day = date[3:] #day
        starttime = row['starttime']
        endtime = row['endtime']
        starttimeDTform = pd.to_datetime(str(year) + '/' + str(date) + " " + str(starttime)) #轉成PD格式的dateTime
        endtimeDTform = pd.to_datetime(str(year) + '/' + str(date) + " " + str(endtime))
        startkilo = float(row['startkilo'])
        endkilo = float(row['endkilo'])

        ### Read Traffic Volumes
        # get ETag GantryID0
        gantryID = MiletoETagGantryConverter.get_equipmentID(inputArgs={'freeway': FREEWAY, 'direction': direction,
                                                                         'startkilo': startkilo, 'endkilo': endkilo})
        trafficVolumes = etagDataParserDict[int(month)][int(day)].get_trafficVolumes(dateTime=starttimeDTform, gantryID=gantryID, direction=direction)

        freewayCSVContentDict[FREEWAY+direction].at[index, 'volume_S'] = trafficVolumes['S']
        freewayCSVContentDict[FREEWAY+direction].at[index, 'volume_L'] = trafficVolumes['L']
        freewayCSVContentDict[FREEWAY+direction].at[index, 'volume_T'] = trafficVolumes['T']
        freewayCSVContentDict[FREEWAY+direction].at[index, 'volume'] = trafficVolumes['volume']
        freewayCSVContentDict[FREEWAY+direction].at[index, 'PCU'] = trafficVolumes['PCU']

        ### Weather data parse
        stationID = MiletoWeatherStationConverter.get_equipmentID(inputArgs={'freeway': FREEWAY, 'direction': direction,
                                                                              'startkilo': startkilo, 'endkilo': endkilo})
        stationName = MiletoWeatherStationConverter.get_equipmentName(inputArgs={'freeway': FREEWAY, 'direction': direction,
                                                                               'startkilo': startkilo, 'endkilo': endkilo})

        ## rain
        rainfall = rainDataParserDict[stationID[:-1]].get_rainfall(startTime=starttimeDTform, endTime=endtimeDTform)
        #stationID 最後多一個0去掉 才是正確檔名
        freewayCSVContentDict[FREEWAY+direction].at[index, 'rain'] = rainfall

        ## windspeed
        windspeed = windDataParserDict[stationName].get_windspeed(endtime=endtimeDTform)
        freewayCSVContentDict[FREEWAY+direction].at[index, 'windspeed'] = windspeed

    # The slowest way
    # for index, row in freewayCSVContentDict[freeway+direction].iterrows():
    #     start(row=row, index=index)

    freewayCSVContentDict[FREEWAY+direction]['index'] = np.arange(0, freewayCSVContentDict[FREEWAY+direction].shape[0])
    freewayCSVContentDict[FREEWAY+direction].apply(start, axis=1, raw=True) #axis = 1 -> tell panda.apply() to iterate each row

    freewayCSVContentDict[FREEWAY+direction].to_csv(str(DOWN_LIMIT) + '_' + str(UPPER_LIMIT) + '.csv', enconding='utf-8-sig')
    print("ALL TASKS DONE!")
    os.system('pause')


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











