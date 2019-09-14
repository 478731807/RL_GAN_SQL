'''
提取跟驰片段（前车ID保持不变，本车的offset没有突变，本车速度最小值大于10）
'''

#coding=utf-8
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import itertools
import math
from sklearn.preprocessing import Imputer
import heartrate
FindPath = r'E:\研一\Distraction Detection\分心驾驶项目数据\newdata\data\driver31'
CF_Path=r'E:\研二\CF'
FileNames = os.listdir(FindPath)

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
    else:
        print("---  There is this folder!  ---")


for file in FileNames:
    print(file)
    dir = os.path.join(FindPath, file)
    FFname = file.replace('.csv', '')
    directory = CF_Path + '\\'+'%s/' % FFname
    mkdir(directory)
    f = open(dir)
    data = pd.read_csv(f, encoding='utf-8', low_memory=False)
    data['time_series'] = range(0, len(data['FOT_Control.Speed']))
    data['Road Scout.Lane_Offset'] = data['Road Scout.Lane_Offset'] / 1000
    data['FOT_Control.Speed'] = data['FOT_Control.Speed'] * 3.6
    nullNum_ID = len(data['SMS.Object_ID_T0'][data['SMS.Object_ID_T0'].isna()])
    nullNum_speed = len(data['FOT_Control.Speed'][data['FOT_Control.Speed']==0])
    if ((nullNum_ID / len(data['SMS.X_Range_T0'])) > 0.5):
        continue
    if ((nullNum_speed / len(data['FOT_Control.Speed'])) > 0.5):
        continue
    ##缺失ID填补
    for a, s in enumerate(data['SMS.Object_ID_T0']):  # a是按顺序0到n的，而不是原始的index
        if (a < len(data['SMS.Object_ID_T0']) - 2) & (a > 1):
            if np.isnan(data['SMS.Object_ID_T0'][a]):
                k = a
                while np.isnan(data['SMS.Object_ID_T0'][k]):
                    k = k + 1
                    if k >= len(data['SMS.Object_ID_T0'])-5:
                        break
                data['SMS.Object_ID_T0'][a] = data['SMS.Object_ID_T0'][k]

        if (a < len(data['FOT_Control.Speed']) - 2) & (a > 1):
            if np.isnan(data['FOT_Control.Speed'][a]):
                k = a
                while np.isnan(data['FOT_Control.Speed'][k]):
                    k = k + 1
                    if k >= len(data['SMS.Object_ID_T0'])-5:
                        break
                data['FOT_Control.Speed'][a] = data['FOT_Control.Speed'][k]

    # 删除含有nan的行
    data=data[np.isnan(data['SMS.Object_ID_T0'])==False]
    data['offset_diff'] = data['Road Scout.Lane_Offset'].diff()
    data['ID_diff'] = data['SMS.Object_ID_T0'].diff()
    data['ID_diff'] = data['SMS.Object_ID_T0'].diff().fillna(0)  # 第一个填0
    data['offset_diff'] = data['offset_diff'].diff().fillna(0)  # 第一个填0
    ## offset大于1.5米的突变认为发生了换道
    lanechange = np.array(data[abs(data['offset_diff']) >= 1.5].index.values)
    ID_change=np.array(data[abs(data['ID_diff']) != 0].index.values)
    G=0
    for index_LC,value_LC in enumerate(lanechange):
        if index_LC<len(lanechange)-1:
            start_LC=value_LC  # 真实index
            end_LC=lanechange[index_LC+1] # 真实index
            ID_in_LC=ID_change[(ID_change>start_LC)&(ID_change<end_LC)]
            if len(ID_in_LC)==0:
                continue
            else:
                chekpoints=np.insert(ID_in_LC,0,start_LC)
                chekpoints = np.insert(chekpoints,len(chekpoints),end_LC)
                starts=[s for s in chekpoints[0:-1]]
                ends=[e for e in chekpoints[1:]]
                for i in range(len(starts)):
                    CF_period = data.loc[starts[i]:ends[i]+1, :]
                    if (ends[i]-starts[i]>100)&(min(CF_period['FOT_Control.Speed'])>10):
                        x = CF_period.to_csv(directory + 'file_%d.csv' % G)
                        G+=1



