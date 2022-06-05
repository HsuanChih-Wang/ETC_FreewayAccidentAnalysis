import csv
import os
import CSVParser

class RebuildCSVFile(CSVParser.CSVParser):
    def __init__(self, fileRoute, fileName, selectedResults):
        super().__init__(fileName=fileName, fileRoute=fileRoute)
        self.selectedResults = selectedResults

    def rebuildResultsCSV(self):

        from copy import deepcopy
        newResultCSV = []
        timeList = []

        #Create TimseList which contains timestamp every 5 minutes
        for hour in range(0, 24, 1):
            for min in range(0, 60, 5):
                timeList.append(str(hour) + ":" + str(min))

        #Append timestamp to each row of a new csv file
        for row in self.selectedResults:
            for starttime, endtime in zip(timeList[0::1], timeList[1::1]):
                newRow = deepcopy(row)  # deepcopy: create a completely new object instead of referencing to the original one
                newResultCSV.append(newRow)
                newResultCSV[-1]['starttime'] = starttime
                newResultCSV[-1]['endtime'] = endtime

        # Write to csv file
        self.writeCSVfile(newFileName=self.fileName + "_new.csv", data=newResultCSV, method='dict')
        print(f'rebuild csv {self.fileRoute} {self.fileName} done!')

class unknownCSVReaderMethod(Exception):
    pass

class Original_File_Parser(CSVParser.CSVParser):

    def __init__(self, fileRoute, fileName):
        super().__init__(fileRoute, fileName)
        self.selectedRows = []

    #override original function
    def readCSVfile(self, method):
        with open(os.path.join(self.fileRoute, self.fileName), 'r', encoding='UTF-8') as file:
            numOfRows = 1
            try:
                if method == 'dict':
                    reader = csv.DictReader(file)
                    for row in reader:
                        if numOfRows == 1 or numOfRows % 25 == 0:  # Record values every 25 line (24 hours in original data)
                            self.selectedRows.append(dict(row))  # Record in a dictionary form
                        numOfRows = numOfRows + 1
                elif method == 'normal':
                    reader = csv.reader(file)
                    for row in reader:
                        if numOfRows == 1 or numOfRows % 25 == 0:
                            self.selectedRows.append(row)
                        numOfRows = numOfRows + 1
                else:
                    raise unknownCSVReaderMethod

            except unknownCSVReaderMethod:
                print(f"the method : {method} is unknown!")


    def clean_Specific_Column_Values(self):
        colunmNames = ['starttime', 'endtime', 'crash', 'windspeed', 'rain', 'Var_windspeed',
                       'Var_rain', 'volume_S', 'volume_L', 'volume_T', 'volume', 'PCU',
                       'Speed_volume', 'Speed_PCU', 'heavy_rate', 'Var_volume', 'Var_PCU',
                       'Var_Speed_volume', 'Var_Speed_PCU']

        for item in self.selectedRows:
            for name in colunmNames:
                item[name] = 0

    def get_SelectedRows(self):
        return self.selectedRows


if __name__ == '__main__':
    orgFileParser = Original_File_Parser(fileRoute=os.path.join('data', '2020'), fileName='國道5號北向.csv')
    orgFileParser.readCSVfile(method='normal') #readCSVfile
    orgFileParser.clean_Specific_Column_Values() #clean original file content
    results = orgFileParser.get_SelectedRows()

    re1 = RebuildCSVFile(fileRoute=os.path.join('data', '109'), fileName='國道5號北向.csv', selectedResults=results)
    re1.rebuildResultsCSV()


