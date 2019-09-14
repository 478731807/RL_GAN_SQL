'''
提取跟驰片段
本车offset没有突变（大于1.5）
雷达识别的横向距离在2m以内的最小值对应的ID
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

FindPath = r'Y:\成员\张一豪\分心驾驶项目数据\newdata\data\driver21'
CF_Path=r'Y:\成员\张一豪\CF_seg'
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
    ### 本车不换道
    data['offset_diff'] = data['Road Scout.Lane_Offset'].diff()
    data['offset_diff'] = data['offset_diff'].diff().fillna(0)  # 第一个填0
    ## offset大于1.5米的突变认为发生了换道
    lanechange = np.array(data[abs(data['offset_diff']) >= 1.5].index.values)
    for index_LC,value_LC in enumerate(lanechange):
        if index_LC<len(lanechange)-1:
            start_LC=value_LC  # 真实index
            end_LC=lanechange[index_LC+1] # 真实index
            CF_period = data.loc[start_LC:end_LC, :].reset_index()  # 此处重新设置行，为了和后面对应
            ### 判断横向距离在2m以内的所有雷达识别车辆
            radar_col_y_range=CF_period.iloc[:,71:79]
            radar_col_y_range[abs(radar_col_y_range)>2]=np.nan
            ## 确定是否有前车
            lines=np.where(np.sum(~np.isnan(radar_col_y_range),1)>0)  ## 所有 有前车的 行
            for i in lines:
                if len(i)==0:
                    continue
                else:
                    ## 与本车纵向距离最近的车ID和雷达编号
                    #print([i for i in lines])
                    #lines=[int(i) for i in lines]
                    lines_list=list()
                    for i in lines:
                        print(i)
                        i=int(i)
                        lines_list.append(i)
                    radar_col_x_range=CF_period.iloc[lines_list,63:71]
                    # 每一行最小值对应的列
                    for i in range(len(radar_col_x_range)):
                        line=radar_col_x_range.loc[i,:]
                        x_range_min=np.min(radar_col_x_range.iloc[i,:])
                        ID_X_closest=line[line==x_range_min].idxmin()




