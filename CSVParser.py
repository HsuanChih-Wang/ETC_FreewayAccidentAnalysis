import csv
import os
import pandas as pd

# 模組設計以"原有處理後資料內容取"為主

colunmName = ['startkilo', 'endkilo', 'year', 'date', 'starttime', 'endtime', 'crash',
              'lane', 'minlane', 'addlane', 'totalwidth', 'lanewidth',
              'inshoulder', 'outshoulder', 'upslope','downslope','upslopelength',
              'downslopelength', 'maxupslope', 'maxdownslope', 'curvelength', 'minradiuslength','minradius',
              'continuouscurve', 'pavement', 'cement', 'interchange', 'tunnellength', 'tunnelin',
              'tunnelout', 'remark', 'one', 'shouderoallow', 'speedlimit', 'camera',
              'service', 'windspeed', 'rain', 'Var_windspeed', 'Var_rain', 'volume_S', 'volume_L',
              'volume_T', 'volume', 'PCU', 'Speed_volume', 'Speed_PCU', 'heavy_rate',
              'Var_volume', 'Var_PCU', 'Var_Speed_volume', 'Var_Speed_PCU']


class CSVParser():

    def __init__(self, fileRoute, fileName):
        self.fileRoute = fileRoute
        self.fileName = fileName
        self.CSVFileContent = []
        self.CSVFileColumnNames = 0

    def __readCSVfile(self, method):
        try:
            with open(os.path.join(self.fileRoute, self.fileName), 'r', encoding='UTF-8') as file:
                if method == 'dict':
                    reader = csv.DictReader(file)
                    for row in reader:
                        self.CSVFileContent.append(dict(row))  # Record in dictionary form
                elif method == 'normal':
                    reader = csv.reader(file)
                    for row in reader:
                        self.CSVFileContent.append(row) #Record in list form
                    self.CSVFileColumnNames = self.CSVFileContent[0]  # first row is column names -> save them to class property
                    self.CSVFileContent.remove(self.CSVFileContent[0])  # remove first row -> column names

        except FileNotFoundError:
            print(f'file directory: {os.path.join(self.fileRoute, self.fileName)} not found!')
            raise FileNotFoundError
        #raise FileNotFoundError

    def readCSVfile(self, **kwargs):

        try:
            path = os.path.join(self.fileRoute, self.fileName)
            self.CSVFileContent = pd.read_csv(path, **kwargs)
            self.CSVFileColumnNames = self.CSVFileContent.columns.values.tolist()

        except FileNotFoundError:
            print(f'file directory: {os.path.join(self.fileRoute, self.fileName)} not found!')
            raise FileNotFoundError

    def __writeCSVfile(self, method: str, newFileName: str, data):
        if method == 'normal':
            with open(os.path.join(self.fileRoute, newFileName), 'w', encoding='UTF-8', newline='') as file:
                writer = csv.writer(file)  # create the csv writer
                writer.writerow(data)  # write a row to the csv file
        elif method == 'dict':
            with open(os.path.join(self.fileRoute, newFileName), 'w', encoding='UTF-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=colunmName)  # create the csv writer
                writer.writerows(data)  # "data" -> a list contains multiple data
        else:
            print("Method does not exist!")

    # def writeCSVfile(self, newfileName, data, **kwargs):
    #     data.to_csv(newfileName, **kwargs)

    def getCSVfileContent(self):
        return self.CSVFileContent

    def getColunmnames(self):
        return self.CSVFileColumnNames

    def columnName_to_index(self, columnName):
        try:
            index = self.CSVFileContent.index(columnName)
        except ValueError:
            print(f"columnName: {columnName} is not existed in the columnNameList {self.CSVFileColumnNames}")
            raise ValueError
        return index