import math;
import random;
from matplotlib import pyplot as plt
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam
import numpy as np
from keras.callbacks import ModelCheckpoint
import os


#采样函数
def sample(low, up, num):
    data = [];
    for i in range(num):
        #采样
        tmp = random.uniform(low, up);
        data.append(tmp);
    data.sort();
    return data;

#sin函数
def func(x):
    y = [];
    for i in range(len(x)):
        tmp = math.sin(x[i] - math.pi/3);
        y.append(tmp);
    return y;

#获取模型拟合结果
def getfit(model,x):
    y = [];
    for i in range(len(x)):
        tmp = model.predict([x[i]], 10);
        y.append(tmp[0][0]);
    return y;

#删除同一目录下的所有文件
def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)

if __name__ == '__main__':
    path = "C:/Users/USER/PycharmProjects/RL/animation_plot/";
    del_file(path);

    low = 0;
    up = 2 * math.pi;
    x = np.linspace(low, up, 1000);
    y = func(x);

    # 数据采样
#     x_sample = sample(low,up,20);
    x_sample = [0.09326442022999694, 0.5812590520508311, 1.040490143783586, 1.5504427746047338, 2.1589557183817036, 2.6235357787018407, 2.712578091093361, 2.7379109336528167, 3.0339662651841186, 3.147676812083248, 3.58596337171837, 3.6621496731124314, 3.81130899864203, 3.833092859928872, 4.396611340802901, 4.4481080339256875, 4.609657879057151, 5.399731063412583, 5.54299720786794, 5.764084730699906];
    y_sample = func(x_sample);

    # callback
    filepath="C:/Users/USER/PycharmProjects/RL/animation_plot/weights-improvement-{epoch:00d}.hdf5";
    checkpoint= ModelCheckpoint(filepath, verbose=1, save_best_only=False, mode='max');
    callbacks_list= [checkpoint];

    # 建立顺序神经网络层次模型
    model = Sequential();
    model.add(Dense(10, input_dim=1, init='uniform', activation='relu'));
    model.add(Dense(1, init='uniform', activation='tanh'));
    adam = Adam(lr = 0.05);
    model.compile(loss='mean_squared_error', optimizer=adam, metrics=['accuracy']);
    model.fit(x_sample, y_sample, nb_epoch=1000, batch_size=20,callbacks=callbacks_list);

    #测试数据
    x_new = np.linspace(low, up, 1000);
    y_new = getfit(model,x_new);

    # 数据可视化
    plt.plot(x,y);
    plt.scatter(x_sample, y_sample);
    plt.plot(x_new,y_new);

    plt.show();