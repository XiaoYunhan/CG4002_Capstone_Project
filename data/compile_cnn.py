import pandas as pd
import os


directory = 'Raw Data/'
labels_path = 'Raw Data/labels.txt'

AXIS = 6
LINES = 42
LINE_LEN = 252

cols = []
for i in range(LINE_LEN + 1):
    cols.append(i)

df3 = pd.DataFrame(columns=cols)

prev_exp = ''
prev_usr = ''

labels = pd.read_csv(labels_path, sep="\s+", header=None)
for index, row in labels.iterrows():
    if row[4] - row[3] < LINES:
        continue
    exp = row[0].astype('U')
    if len(exp) == 1:
        exp = '0'+ exp
    usr = row[1].astype('U')
    if len(usr) == 1:
        usr = '0'+ usr
    if exp != prev_exp or usr != prev_usr:
        file = directory + r'exp' + exp + "_user" + usr + ".txt"
        df = pd.read_csv(file, sep="\s+", names=['accX', 'accY', 'accZ', 'gyroX', 'gyroY', 'gyroZ'])
    #end =  row[4] - ((row[4] - row[3]) % 10)
    df2 = df.iloc[[row[3]]]
    for i in range(LINES - 1):
        next_row = df.iloc[[row[3]+i+1]]
        df2 = pd.concat([df2.reset_index(drop=True), next_row.reset_index(drop=True)], axis=1, ignore_index=True)
    df2.at[0, LINE_LEN] = row[2]
    df2 = df2.astype({LINE_LEN: int})
    df3 = df3.append(df2)
    


    for i in range(row[4] - row[3] - LINES - 1):
        #print(row[3]+i+10, df.shape)
        
        if row[3]+i+LINES >= df.shape[0]:
            break
        df2.drop(df2.columns[[0,1,2,3,4,5,LINE_LEN]], axis=1, inplace=True)
        next_row = df.iloc[[row[3]+i+LINES]]
        df2 = pd.concat([df2.reset_index(drop=True), next_row.reset_index(drop=True)], axis=1, ignore_index=True)
        df2.at[0, LINE_LEN] = int(row[2])
        df2 = df2.astype({LINE_LEN: int})
        df3 = df3.append(df2)
    #print (row[0], row[1])
    
df3.to_csv(directory + '/compiled_cnn.txt', header=None, index=None, sep=' ', mode='w')
        