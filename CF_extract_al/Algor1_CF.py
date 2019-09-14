'''
提取跟驰片段(效果不佳）
本车offset没有突变（大于1.5）
雷达T0识别的前车ID不变
雷达T0识别的横向距离在2m以内
大于15s，纵向距离在100以内，本车速度在20km以上
'''

#coding=utf-8
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import itertools
import math
from sklearn.preprocessing import Imputer

FindPath = r'Y:\成员\一豪又去识别人脸了\分心驾驶项目数据\newdata\data\driver21'
CF_Path=r'Y:\成员\一豪又去识别人脸了\CF_seg'
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
    copy_data=data.copy()
    nullNum_ID = len(data['SMS.Object_ID_T0'][data['SMS.Object_ID_T0'].isna()])
    nullNum_speed = len(data['FOT_Control.Speed'][data['FOT_Control.Speed']==0])
    ## 若数据缺失比例大于50%，则跳过
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
                    CF_period = data.loc[starts[i]:ends[i]+1, :].reset_index()
                    CF_period_copy=copy_data.loc[starts[i]:ends[i]+1, :].reset_index()
                    #### 判断，避免大面积修补
                    nullNum_ID = len(CF_period_copy['SMS.Object_ID_T0'][CF_period_copy['SMS.Object_ID_T0'].isna()])
                    nullNum_speed = len(CF_period['FOT_Control.Speed'][CF_period['FOT_Control.Speed'] == 0])
                    ## 若数据缺失比例大于20%，则跳过
                    if ((nullNum_ID / len(CF_period_copy['SMS.X_Range_T0'])) > 0.2):
                        continue
                    if ((nullNum_speed / len(CF_period['FOT_Control.Speed'])) > 0.2):
                        continue
                    ###### 关键特征缺失值填补
                    for a, s in enumerate(CF_period['FOT_Control.Speed']):  # a是按顺序0到n的，而不是原始的index
                        if (a < len(CF_period['FOT_Control.Speed']) - 2) & (a > 1):
                            if np.isnan(CF_period['FOT_Control.Speed'][a]):
                                k = a
                                while np.isnan(CF_period['FOT_Control.Speed'][k]):
                                    k = k + 1
                                    if k >= len(CF_period['FOT_Control.Speed']) - 5:
                                        break
                                CF_period['FOT_Control.Speed'][a] = (CF_period['FOT_Control.Speed'][a - 1] +
                                                                    CF_period['FOT_Control.Speed'][k]) / 2
                            if np.isnan(CF_period['SMS.X_Range_T0'][a]):
                                k = a
                                while np.isnan(CF_period['SMS.X_Range_T0'][k]):
                                    k = k + 1
                                    if k >= len(CF_period['SMS.X_Range_T0']) - 5:
                                        break
                                CF_period['SMS.X_Range_T0'][a] = (CF_period['SMS.X_Range_T0'][a - 1] +
                                                                    CF_period['SMS.X_Range_T0'][k]) / 2
                            if np.isnan(CF_period['SMS.Y_Range_T0'][a]):
                                k = a
                                while np.isnan(CF_period['SMS.Y_Range_T0'][k]):
                                    k = k + 1
                                    if k >= len(CF_period['SMS.Y_Range_T0']) - 5:
                                        break
                                CF_period['SMS.Y_Range_T0'][a] = (CF_period['SMS.Y_Range_T0'][a - 1] +
                                                                    CF_period['SMS.Y_Range_T0'][k]) / 2

                    if (ends[i]-starts[i]>150)&(min(CF_period['FOT_Control.Speed'])>20)&(max(CF_period['SMS.X_Range_T0'])<100):
                        ##片段时长大于15s，最小速度大于20km/h,最大纵向距离小于100m
                        # T0识别的横向距离在2m以内
                        if max(abs(CF_period['SMS.Y_Range_T0']))<=2:
                            x = CF_period.to_csv(directory + 'file_%d.csv' % G)
                            G+=1



