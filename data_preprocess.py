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

etagDataParserDict = {}
VD_DataParserDict = {}


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

class NotFindEtagDataIndexError(Exception):

    def __init__(self, inputArgs: dict, message="Can not find Etag Index : "):
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

    directionTransform = {'北': '北向', '南': '南向', '東': '東向', '西': '西向'}

    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName) #Input: Reference File
        super().readCSVfile()

    def get_VDID(self, inputArgs: dict) -> list:
        """inputArgs = ['freeway': a, 'direction':b, 'startkilo':c, 'endkilo':d]"""

        c1 = (self.CSVFileContent.freeway == inputArgs['freeway'])
        c2 = (self.CSVFileContent.direction == inputArgs['direction'])
        c3 = (self.CSVFileContent.startkilo == inputArgs['endkilo'])
        c4 = (self.CSVFileContent.endkilo == inputArgs['startkilo'])
        # 注意: 此處 Startkilo 和 endkilo 設備對照表中 反過來才是正確的

        index = (c1 & c2 & c3 & c4).idxmax()
        VDID = self.CSVFileContent.at[index, 'VDID']
        backup_VDID = self.CSVFileContent.at[index, 'Backup_VDID']

        if VDID and backup_VDID:
            return [VDID, backup_VDID]
        else:
            raise NotFindEquipmentIDError(inputArgs=inputArgs)


    def get_EtagEquipmentID(self, inputArgs: dict) -> list:
        """inputArgs = ['freeway': a, 'direction':b, 'startkilo':c, 'endkilo':d]"""
        inputArgs['direction'] = MileToEquipementIDConverter.directionTransform[inputArgs['direction']]

        c1 = (self.CSVFileContent.freeway == inputArgs['freeway'])
        c2 = (self.CSVFileContent.direction == inputArgs['direction'])
        c3 = (self.CSVFileContent.startkilo == inputArgs['endkilo'])
        c4 = (self.CSVFileContent.endkilo == inputArgs['startkilo'])
        # 注意: 此處 Startkilo 和 endkilo 設備對照表中 反過來才是正確的

        index = (c1 & c2 & c3 & c4).idxmax()
        equipmentID = self.CSVFileContent.at[index, 'equipmentID']
        equipmentID_nextGantry = self.CSVFileContent.at[index+1, 'equipmentID']

        if equipmentID == '01F0376N' or equipmentID_nextGantry == '01F0467N':
            print('xxxx')

        while equipmentID_nextGantry == equipmentID:
            index = index + 1
            equipmentID_nextGantry = self.CSVFileContent.at[index, 'equipmentID']

        if equipmentID:
            return [equipmentID, equipmentID_nextGantry]
        else:
            raise NotFindEquipmentIDError(inputArgs=inputArgs)

    def get_equipmentName(self, inputArgs: dict):
        """inputArgs = ['freeway': a, 'direction':b, 'startkilo':c, 'endkilo':d]"""

        inputArgs['direction'] = MileToEquipementIDConverter.directionTransform[inputArgs['direction']]
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


class TrafficDataParser(CSVParser.CSVParser):

    PCU = {'S': 1.0, 'L': 1.6, 'T': 2.0}

    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute=fileRoute, fileName=fileName)
        self.trafficVolumeDict = {'S': 0, 'L': 0, 'T': 0, 'volume': 0, 'PCU': 0.0,
                                  'Speed_PCU': 0.0, 'Speed_volume': 0.0,
                                  'Var_PCU': 0.0, 'Var_Speed_PCU': 0.0, 'Var_Speed_Volume': 0.0, 'Var_volume': 0.0,
                                  'heavy_rate': 0.0}

        self.trafficSpaceSpeedDict = {'S': 0.0, 'L': 0.0, 'T': 0.0, 'Avg': 0.0, 'Median': 0.0}

        self.readCSVfile()

    def get_PCU_Volumes(self):
        PCE = TrafficDataParser.PCU['S'] * self.trafficVolumeDict['S'] + \
              TrafficDataParser.PCU['T'] * self.trafficVolumeDict['T'] + \
              TrafficDataParser.PCU['L'] * self.trafficVolumeDict['L']
        return PCE

    def get_totalTrafficVolumes(self):
        totalVolume = self.trafficVolumeDict['S'] + self.trafficVolumeDict['L'] + self.trafficVolumeDict['T']
        return totalVolume

    def get_heavyRate(self):
        heavyVehicleVolume = self.trafficVolumeDict['L'] + self.trafficVolumeDict['T']
        totalVolume = self.trafficVolumeDict['L'] + self.trafficVolumeDict['T'] + self.trafficVolumeDict['S']

        try:
            heavyRate = round((heavyVehicleVolume / totalVolume), 3)
        except ZeroDivisionError:
            print(f"ZeroDivisionError! round({heavyVehicleVolume} / {totalVolume}, 3)")
            heavyRate = 0

        return heavyRate

    def get_avg_SpaceSpeed(self):
        result = np.mean(np.array([self.trafficSpaceSpeedDict['S'],
                          self.trafficSpaceSpeedDict['L'],
                          self.trafficSpaceSpeedDict['T']]))

        return round(result, 1)

    def get_median_SpaceSpeed(self):
        result = np.median(np.array([self.trafficSpaceSpeedDict['S'],
                                     self.trafficSpaceSpeedDict['L'],
                                     self.trafficSpaceSpeedDict['T']]))

        return round(result, 1)

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
            raise NotFindEtagDataIndexError(inputArgs={'dateTime': dateTime.strftime("%Y-%m-%d %H:%M"), 'gantryID': gantryID, 'direction': direction})

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
        '''EXAMPLE:
        dateTime = %Y-%m-%d %H:%M
        Direction = 北
        '''

        tempResults = {'5': 0, '31': 0, '32': 0, '41': 0, '42': 0}  # five types of vehicles
        directionEng = covertDirectionToEng[direction]  # translate direction in Chinese to English

        c1 = (self.CSVFileContent['TimeInterval'] == dateTime.strftime("%Y-%m-%d %H:%M"))
        c2 = (self.CSVFileContent['GantryID'] == gantryID)
        c3 = (self.CSVFileContent['Direction'] == directionEng)
        indexList = self.CSVFileContent.index[(c1 & c2 & c3)].tolist()

        if not indexList:
            raise NotFindEtagDataIndexError(inputArgs={'dateTime': datetime, 'gantryID': gantryID, 'direction': direction})

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
        self.trafficVolumeDict['heavy_rate'] = self.get_heavyRate()

        return self.trafficVolumeDict

    def get_trafficVolumesFromVD(self):



        return 0


    def get_trafficSpaceSpeed(self, dateTime: datetime, gantryFrom: str, gantryTo: str) -> dict:
        '''EXAMPLE:
        dateTime = %Y-%m-%d %H:%M
        Direction = 北
        '''
        tempResults = {'5': 0, '31': 0, '32': 0, '41': 0, '42': 0}  # five types of vehicles
        c1 = (self.CSVFileContent['TimeInterval'] == dateTime.strftime("%Y/%m/%d %H:%M"))
        c2 = (self.CSVFileContent['GantryFrom'] == gantryFrom)
        c3 = (self.CSVFileContent['GantryTo'] == gantryTo)
        indexList = self.CSVFileContent.index[(c1 & c2 & c3)].tolist()

        if not indexList:
            #特別修bug用
            if gantryFrom == '01F0509N' and gantryTo == '01F0467N':
                gantryFrom = '01F0511N'
                c1 = (self.CSVFileContent['TimeInterval'] == dateTime.strftime("%Y/%m/%d %H:%M"))
                c2 = (self.CSVFileContent['GantryFrom'] == gantryFrom)
                c3 = (self.CSVFileContent['GantryTo'] == gantryTo)
                indexList = self.CSVFileContent.index[(c1 & c2 & c3)].tolist()
            else:
                raise NotFindEtagDataIndexError(inputArgs={'dateTime': dateTime.strftime("%Y-%m-%d %H:%M"),
                                                           'gantryFrom': gantryFrom,
                                                           'gantryTo': gantryTo,
                                                           'direction': direction})
        vehTypeList = []
        spaceSpeedList = []

        for index in indexList:
            vehTypeList.append(self.CSVFileContent.at[index, 'VehicleType'])
            spaceSpeedList.append(self.CSVFileContent.at[index, 'SpaceMeanSpeed'])

        for i in np.arange(5):  # five types of vehicle: 5, 31, 32, 41, 42
            tempResults.update({str(vehTypeList[i]): spaceSpeedList[i]})

        self.trafficSpaceSpeedDict['S'] = np.mean(np.array([int(tempResults['31']), int(tempResults['32'])]))
        self.trafficSpaceSpeedDict['L'] = np.mean(np.array([int(tempResults['41']), int(tempResults['42'])]))
        self.trafficSpaceSpeedDict['T'] = float(tempResults['5'])
        self.trafficSpaceSpeedDict['Avg'] = self.get_avg_SpaceSpeed()
        self.trafficSpaceSpeedDict['Median'] = self.get_median_SpaceSpeed()

        return self.trafficSpaceSpeedDict

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
        self.CSVFileContent['時間'] = self.CSVFileContent['時間'].replace(['24:00:00'], '00:00') #一個坑: replace "24:00:00" with "00:00"
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
    START_ROW = 4900001  #Please start from ROW 1!! not row 0 -> becasue ROW 0 is added in the subfunction!
    END_ROW = 5000000  #5546276 #5042301
    MONTH = 12
    TO_CSV_PATH = os.path.join("output", YEAR + '_' + FREEWAY + '_' + str(START_ROW) + '_' + str(END_ROW) + '.csv')

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

    def store_etagCSVData(year: str, type: str):
        etagDataParserDict.update({type: {}})
        for month in np.arange(1, MONTH + 1):  # Month 1~12
            numberOfDays = calendar.monthrange(int(YEAR), month)[1] #retrive the number of days of a specific month
            etagDataParserDict[type].update({month: {}})
            for day in np.arange(1, numberOfDays + 1):
                MonthInString = str(int(month))+'月'
                ETC_Data_Route = os.path.join('data', 'Etag', type, year, MonthInString)
                ETCDataName = str(int(day))+'日.csv'
                ETCDataParser = TrafficDataParser(fileRoute=ETC_Data_Route, fileName=ETCDataName)
                etagDataParserDict[type][month].update({day: ETCDataParser})
        print(f"Load ETAG DATA : {type} DONE!")
        return 0

    def store_VD_Data(year: str, month: str, day: str):
        MonthInString = str(int(month))+'月'
        VD_Data_Route = os.path.join('data', 'VD', year, MonthInString)
        VD_DataName = str(int(day))+'日.csv'
        VD_DataParser = TrafficDataParser(fileRoute=VD_Data_Route, fileName=VD_DataName)
        VD_DataParserDict.update({day: VD_DataParser})

    def change_colTypes():
        COL_TO_FLOAT_LIST = ['PCU', 'heavy_rate', 'Speed_PCU', 'Speed_volume',
                             'windspeed', 'rain', 'minradius', 'minradiuslength',
                             'continuouscurve']

        for col in COL_TO_FLOAT_LIST:
            freewayCSVContentDict[FREEWAY+direction][col] \
                = freewayCSVContentDict[FREEWAY+direction][col].astype(float)
        print(f"CHANGE COLUMN TYPE OF {COL_TO_FLOAT_LIST}  TO FLOAT DONE!")
        return 0

    def generate_skiprows(startRow: int, endRow: int) -> np.ndarray:
        originalNumberOfRows = csvParser.get_CSVFileOriginalNumberOfRows()
        allRows = np.array([i for i in np.arange(originalNumberOfRows+1)])
        wantedRows = np.array([0] + [i for i in np.arange(startRow, endRow+1)])  # [0] -> row of column names
        skipRows = np.delete(allRows, wantedRows)
        print(f"WANTED ROWS = 0, {startRow} ~ {endRow}")
        return skipRows

    #route = os.path.join('data', YEAR, 'newCombinedCSV') #read: after combined CSV
    route = os.path.join('data', YEAR, '5min') #read: after combined CSV
    csvParser = CSVParser.CSVParser(fileRoute=route, fileName=FREEWAY + '_' + direction + '_alreadyHasVolumeWeather.csv')
    skipRows = generate_skiprows(startRow=START_ROW, endRow=END_ROW) #set the rows that are required to skip
    csvParser.readCSVfile(skiprows=skipRows)
    ##skiprows=[i for i in range(1, 5042300)]
    ## usecols=['startkilo', 'endkilo', 'year', 'date', 'starttime', 'endtime']

    freewayCSVContentDict[FREEWAY+direction] = csvParser.getCSVfileContent()  # get the content of the csv
    change_colTypes()  # convert column types
    freewayCSVColumnNames = csvParser.getColunmnames()

    print(f"input file length = {len(freewayCSVContentDict[FREEWAY+direction])}")
    print("SAVE SUCCESS!")

    ## Read Mile to gantryID or stationID convert file
    MiletoETagGantryConverter = MileToEquipementIDConverter(fileRoute=os.path.join('data', 'MileToGantryReference'),
                                                            fileName='ETC點位對照表_2公里_20220716.csv')

    Mileto_VD_EquipmentConverter = MileToEquipementIDConverter(fileRoute=os.path.join('data', 'MileToGantryReference'),
                                                            fileName='VD點位對照表_2公里_20220119.csv')

    MiletoWeatherStationConverter = MileToEquipementIDConverter(fileRoute=os.path.join('data', 'MileToGantryReference'),
                                                                fileName='天氣測站對照表_2公里_2019_2020.csv')

    # store_rainCSVData()  #儲存雨量測站表
    # store_windCSVData()  #儲存風向測站表
    # store_etagCSVData(year=YEAR, type='M03') #儲存etag M03資料


    def start(row):
        index = row['index']
        print(f'startRow={START_ROW} endRow={END_ROW} index = {index}')

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

        #### get ETag GantryID
        #gantryIDFindResult = MiletoETagGantryConverter.get_EtagEquipmentID(inputArgs={'freeway': FREEWAY, 'direction': direction,
        #                                                                'startkilo': startkilo, 'endkilo': endkilo})
        #gantryID = gantryIDFindResult[0]
        #next_GantryID = gantryIDFindResult[1]

        VDID_FindResult = Mileto_VD_EquipmentConverter.get_VDID(inputArgs={'freeway': FREEWAY, 'direction': direction,
                                                                          'startkilo': startkilo, 'endkilo': endkilo})

        def read_TrafficVolume():
            ### Read Traffic Volumes

            trafficVolumes = etagDataParserDict['M03'][int(month)][int(day)].get_trafficVolumes(dateTime=starttimeDTform,
                                                                                                gantryID=gantryID,
                                                                                                direction=direction)
            freewayCSVContentDict[FREEWAY+direction].at[index, 'volume_S'] = trafficVolumes['S']
            freewayCSVContentDict[FREEWAY+direction].at[index, 'volume_L'] = trafficVolumes['L']
            freewayCSVContentDict[FREEWAY+direction].at[index, 'volume_T'] = trafficVolumes['T']
            freewayCSVContentDict[FREEWAY+direction].at[index, 'volume'] = trafficVolumes['volume']
            freewayCSVContentDict[FREEWAY+direction].at[index, 'PCU'] = trafficVolumes['PCU']
            freewayCSVContentDict[FREEWAY+direction].at[index, 'heavy_rate'] = trafficVolumes['heavy_rate']

        def read_TrafficVolumeFromVD():
            ###
            store_VD_Data(year=YEAR, month=month, day=day)
            VD_DataParserDict[day].get_trafficVolumesFromVD(time, )

        def read_WeatherData():
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
            try:
                freewayCSVContentDict[FREEWAY+direction].at[index, 'windspeed'] = windspeed
            except ValueError:
                print(f"ValueError! START_ROW={START_ROW}, ENDROW={END_ROW}"
                      f"windspeed = {windspeed}, index={index}, stationName={stationName}, endTimeDTform = {endtimeDTform}")
                raise ValueError

        def read_TrafficSpeed():
            if direction == '北':
                trafficSpeed = etagDataParserDict['M04'][int(month)][int(day)].get_trafficSpaceSpeed(dateTime=starttimeDTform,
                                                                                      gantryFrom=next_GantryID,
                                                                                      gantryTo=gantryID)

                freewayCSVContentDict[FREEWAY+direction].at[index, 'SpaceSpeed_S'] = trafficSpeed['S']
                freewayCSVContentDict[FREEWAY+direction].at[index, 'SpaceSpeed_L'] = trafficSpeed['L']
                freewayCSVContentDict[FREEWAY+direction].at[index, 'SpaceSpeed_T'] = trafficSpeed['T']
                freewayCSVContentDict[FREEWAY+direction].at[index, 'AvgSpaceSpeed'] = trafficSpeed['Avg']
                freewayCSVContentDict[FREEWAY+direction].at[index, 'MedianSpaceSpeed'] = trafficSpeed['Median']

            return 0

        read_TrafficSpeed()


    freewayCSVContentDict[FREEWAY+direction]['index'] = np.arange(0, freewayCSVContentDict[FREEWAY+direction].shape[0])
    freewayCSVContentDict[FREEWAY+direction].apply(start, axis=1, raw=True) #axis = 1 -> tell panda.apply() to iterate each row

    freewayCSVContentDict[FREEWAY+direction].to_csv(TO_CSV_PATH, encoding='utf-8-sig')
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











