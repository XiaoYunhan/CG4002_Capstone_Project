import pandas as pd
import os

directory = 'HAPT Dataset/RawData'
labels_path = 'HAPT Dataset/RawData/labels.txt'

df_list = []
prev_exp = ''
prev_usr = ''

labels = pd.read_csv(labels_path, sep="\s+", header=None)
for index, row in labels.iterrows():
    exp = row[0].astype('U')
    if len(exp) == 1:
        exp = '0'+ exp
    usr = row[1].astype('U')
    if len(usr) == 1:
        usr = '0'+ usr
    if exp != prev_exp or usr != prev_usr:
        acc_file = directory + r'/acc_exp' + exp + "_user" + usr + ".txt"
        gyro_file = directory + r'/gyro_exp' + exp + "_user" + usr + ".txt"
        acc = pd.read_csv(acc_file, sep="\s+", names=['accX', 'accY', 'accZ'])
        gyro = pd.read_csv(gyro_file, sep="\s+", names=['gyroX', 'gyroY', 'gyroZ'])
    end =  row[4] - ((row[4] - row[3]) % 64)
    acc_sample = acc.iloc[row[3]:end]
    gyro_sample = gyro.iloc[row[3]:end]
    gyro_sample['Activity'] = row[2]
    df = pd.concat([acc_sample, gyro_sample], axis=1)
    df_list.append(df)
    prev_exp = exp
    prev_usr = usr

out = pd.concat(df_list)

out.to_csv(directory + '/raw.txt', header=None, index=None, sep=' ', mode='w')



