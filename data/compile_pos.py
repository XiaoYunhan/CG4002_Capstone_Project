import pandas as pd
import os, random, string
from tqdm import tqdm
import multiprocessing


def process_labels(labels):
    AXIS = 6
    LINES = 10
    LINE_LEN = 60
    cols = []
    for i in range(LINE_LEN + 1):
        cols.append(i)

    df3 = pd.DataFrame(columns=cols)

    prev_exp = ''
    prev_usr = ''

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
            file = directory + r'/pos' + exp + "_user" + usr + ".txt"
            df = pd.read_csv(file, sep="\s+", names=['accX', 'accY', 'accZ', 'gyroX', 'gyroY', 'gyroZ'])
        #print(row[3], df.shape)
        df2 = df.iloc[[row[3]]]
        for i in range(LINES - 1):
            #print(row[3]+i+1, df.shape)
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
    df3.to_csv(directory + 'compiled_pos.txt', header=None, index=None, sep=' ', mode='w')

directory = 'Raw Data/positions/'
labels_path = directory + 'labels.txt'
chunks = pd.read_csv(labels_path, sep="\s+", header=None)
process_labels(chunks)
# num_processes = multiprocessing.cpu_count()

# chunks = pd.read_csv(labels_path, sep="\s+", header=None, chunksize=14)
# pool = multiprocessing.Pool(num_processes)
# pd.concat(pool.map(process_labels, chunks))
# pool.close()
# pool.join()
# li = []
# for entry in os.listdir(os.getcwd() + '/' + directory + 'tmp'):
#    li.append(pd.read_csv(directory + 'tmp/' + entry, sep="\s+", header=None))
#    os.unlink(os.getcwd() + '/' + directory + 'tmp' + entry)

# df = pd.concat(li, axis=0, ignore_index=True)
# df.to_csv(directory + '/compiled_pos.txt', header=None, index=None, sep=' ', mode='w')
