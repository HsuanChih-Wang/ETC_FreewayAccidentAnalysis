
import numpy as np
import pandas as pd
from sklearn import svm, metrics
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split, cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns


def convert_dtype(x):
    if not x:
        return ''
    try:
        return str(x)
    except:
        return ''

def draw_figures():
    sns.set_style('whitegrid')
    fig, ax = plt.subplots()
    data['windspeed'].hist(ax=ax, bins=100)
    #ax.set_yscale('log')
    ax.tick_params(labelsize=14)
    ax.set_xlabel('windspeed', fontsize=14)
    ax.set_ylabel('occurence', fontsize=14)
    #plt.show()

def get_count(x: pd.core.frame.DataFrame) -> int:
    return x.shape[0]

#pd.read_csv('file.csv',converters={'first_column': convert_dtype,'second_column': convert_dtype})


# Load ------------------------------------------
data = pd.read_csv("data/freeway_no1_north.csv")
# Preprocessing -----------------
print(data.columns)

print(data['cement'])
data.drop(['pavement', 'cement', 'remark', 'upslope', 'downslope', 'minradiuslength',
           'one', 'Var_windspeed', 'Var_rain', 'volume', 'Var_volume', 'Var_PCU',
           'Var_Speed_volume', 'Var_Speed_PCU'], axis=1, inplace=True)
print(data.columns)
data.drop(['startkilo', 'endkilo', 'year', 'date', 'starttime', 'endtime'], axis=1, inplace=True)

# replace crash values
data.loc[data["crash"] >= 1, "crash"] = 1 #convert crash values to 1
# data['rain'] has many non-numeric values: "&", try to fix them
data['rain'] = pd.to_numeric(data['rain'], errors='coerce').fillna(0, downcast='float')
data['windspeed'] = pd.to_numeric(data['windspeed'], errors='coerce').fillna(0, downcast='float')
data['Speed_volume'] = pd.to_numeric(data['Speed_volume'], errors='coerce').fillna(0, downcast='float')
data['Speed_PCU'] = pd.to_numeric(data['Speed_PCU'], errors='coerce').fillna(0, downcast='float')
data['heavy_rate'] = pd.to_numeric(data['heavy_rate'], errors='coerce').fillna(0, downcast='float')

print(data.dtypes)

#Convert to categorial type..................
data["crash"] = data["crash"].astype("category")
data["minlane"] = data["minlane"].astype("category")
data["addlane"] = data["addlane"].astype("category")
data["continuouscurve"] = data["continuouscurve"].astype("category")
data["interchange"] = data["interchange"].astype("category")
data["tunnelin"] = data["tunnelin"].astype("category")
data["tunnelout"] = data["tunnelout"].astype("category")
data["shouderoallow"] = data["shouderoallow"].astype("category")
data["camera"] = data["camera"].astype("category")
data["service"] = data["service"].astype("category")

get_count(data[data['windspeed'] == 2])


## Correlation heatmap 變數相關性確認
print(data.corr())
plt.figure(figsize=(len(data.columns), len(data.columns)))
sns.heatmap(data.corr(),annot=True, cmap='coolwarm')
plt.show() #畫出熱力圖

data_sample = data.sample(n=2000)
data_sample_Y = data['crash']
data_sample_X = data.iloc[:, 1:]

print("data_sample = \n",data_sample)
print("data_Y = \n", data_sample_Y)
print("data_X = \n", data_sample_X)


## Logistic Regression

LRmodel = LogisticRegression(solver='liblinear', random_state=0).fit(data_sample_X, data_sample_Y)

