import pandas as pd
import numpy as np

import os
import calendar

YEAR = '2020'
referenceFile = 'VD點位對照表_2公里_20220716.csv'
vdReferenceFile = pd.read_csv(os.path.join('data', 'MileToGantryReference', referenceFile))

vdidList = vdReferenceFile[(vdReferenceFile.freeway == '國道1號') & (vdReferenceFile.direction == '北向')]['VDID']
backupVDidList = vdReferenceFile[(vdReferenceFile.freeway == '國道1號') & (vdReferenceFile.direction == '北向')]['Backup_VDID']


for month in range(1, 13):
    numberOfDays = calendar.monthrange(int(YEAR), month)[1]
    for day in np.arange(1, numberOfDays + 1):
        reservedIDList = []
        MonthInString = str(int(month))+'月'
        VD_Data_Route = os.path.join('data', 'VD', YEAR, MonthInString)
        VDDataName = str(int(day))+'日.csv'
        TO_CSV_PATH = os.path.join('data', 'VD', YEAR, MonthInString, str(int(day)) + '日_new.csv')

        VDfile = pd.read_csv(os.path.join(VD_Data_Route, VDDataName), encoding='Big5')

        for vdid in vdidList:
            indexList = VDfile[VDfile.vdid == vdid].index.to_list()
            reservedIDList.extend([i for i in indexList])

        for vdid in backupVDidList:
            indexList = VDfile[VDfile.vdid == vdid].index.to_list()
            reservedIDList.extend([i for i in indexList])

        allRows = np.arange(len(VDfile))
        dropRows = np.delete(allRows, reservedIDList)

        VDfile.drop(VDfile.index[dropRows], inplace=True)

        VDfile.to_csv(TO_CSV_PATH, encoding='utf-8', index=False)

        print(f"month {month}, day {day} done!")