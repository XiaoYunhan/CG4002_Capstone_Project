import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

import torch
from torch.utils.data import Dataset, WeightedRandomSampler

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split 

## Loading Raw Data / Features
def import_data(data_path, DATA_LEN):
    cols = []
    for i in range(DATA_LEN + 1):
        cols.append(i)

    df = pd.read_csv(data_path, sep='\s+', names=cols)
    X = df.loc[:, :DATA_LEN-1]
    Y = df.loc[:, DATA_LEN:]
   
    print("Data Loaded from File")
    return X, Y

# Map enumerated classes to start from 0
def remap_classes(Y):
    class_id = {
        1:0,            
        2:1,   
        3:2, 
        4:3,            
        5:4,           
        6:5,             
        7:6,       
        8:7,       
        9:8,         
        10:9,         
        11:10,       
        12:11,       
    }

    id_class = {v: k for k, v in class_id.items()}
    Y['Activity'].replace(class_id, inplace=True)

    return Y, id_class

def split_dataset(X, Y):
    # Split into trainval and test
    #Stratified split allows us to make sure there is good spread of classes across 3 sets
    X_trainval, X_test, Y_trainval, Y_test = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=69)

    # Split trainval into train and val
    X_train, X_val, Y_train, Y_val = train_test_split(X_trainval, Y_trainval, test_size=0.1, stratify=Y_trainval, random_state=21)


    ## Normalise data to scale between 0 and 1
    #scaler = MinMaxScaler()
    #X_train = scaler.fit_transform(X_train)
    #X_val = scaler.transform(X_val)
    #X_test = scaler.transform(X_test)
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    X_val, Y_val = np.array(X_val), np.array(Y_val)
    X_test, Y_test = np.array(X_test), np.array(Y_test)

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(25,7))
    # Train
    sns.barplot(data = pd.DataFrame.from_dict([get_class_distribution(Y_train)]).melt(), x = "variable", y="value", hue="variable",  ax=axes[0]).set_title('Class Distribution in Train Set')
    # Validation
    sns.barplot(data = pd.DataFrame.from_dict([get_class_distribution(Y_val)]).melt(), x = "variable", y="value", hue="variable",  ax=axes[1]).set_title('Class Distribution in Val Set')
    # Test
    sns.barplot(data = pd.DataFrame.from_dict([get_class_distribution(Y_test)]).melt(), x = "variable", y="value", hue="variable",  ax=axes[2]).set_title('Class Distribution in Test Set')

    #plt.savefig("plot.png")
    return X_train, X_val, X_test, Y_train, Y_val, Y_test


## Plot Database spread across classes
def get_class_distribution(obj):
    count_dict = {
        "rating_1": 0,
        "rating_2": 0,
        "rating_3": 0,
        "rating_4": 0,
        "rating_5": 0,
        "rating_6": 0,
        "rating_7": 0,
        "rating_8": 0,
        "rating_9": 0,
        "rating_10": 0,
        "rating_11": 0,
        "rating_12": 0
    }
    
    for i in obj:
        if i == 0: 
            count_dict['rating_1'] += 1
        elif i == 1: 
            count_dict['rating_2'] += 1
        elif i == 2: 
            count_dict['rating_3'] += 1
        elif i == 3: 
            count_dict['rating_4'] += 1
        elif i == 4: 
            count_dict['rating_5'] += 1  
        elif i == 5: 
            count_dict['rating_6'] += 1
        elif i == 6: 
            count_dict['rating_7'] += 1   
        elif i == 7: 
            count_dict['rating_8'] += 1                 
        elif i == 8: 
            count_dict['rating_9'] += 1   
        elif i == 9: 
            count_dict['rating_10'] += 1   
        elif i == 10: 
            count_dict['rating_11'] += 1   
        elif i == 11: 
            count_dict['rating_12'] += 1   
        else:
            print("Check classes.")
            
    return count_dict

## Form DataFrames - converting numpy arrays into tensors
class ClassifierDataset(Dataset):
    
    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data
        
    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]
        
    def __len__ (self):
        return len(self.X_data)

def form_dataframes(X_train, Y_train, X_val, Y_val, X_test, Y_test):
    train_dataset = ClassifierDataset(torch.from_numpy(X_train).float(), torch.from_numpy(Y_train).long())
    val_dataset = ClassifierDataset(torch.from_numpy(X_val).float(), torch.from_numpy(Y_val).long())
    test_dataset = ClassifierDataset(torch.from_numpy(X_test).float(), torch.from_numpy(Y_test).long())

    ## Weighted Sampling
    # Calculate weight of classes in dataset, ensure each batch passed
    # to model during training contains good spread of all classes to reduce over-fitting

    target_list = []
    for _, t in train_dataset:
        target_list.append(t)
        
    target_list = torch.tensor(target_list)
    target_list = target_list[torch.randperm(len(target_list))]

    class_count = [i for i in get_class_distribution(Y_train).values()]
    class_weights = 1.0/torch.tensor(class_count, dtype=torch.float) 
    class_weights_all = class_weights[target_list]

    weighted_sampler = WeightedRandomSampler(
        weights=class_weights_all,
        num_samples=len(class_weights_all),
        replacement=True
    )

    return train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights

def load_dataset(data_path, DATA_LEN):
    X, Y = import_data(data_path, DATA_LEN)
    #Y, id_class = remap_classes(Y)
    X_train, X_val, X_test, Y_train, Y_val, Y_test = split_dataset(X, Y)
    train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights = form_dataframes(X_train, Y_train, X_val, Y_val, X_test, Y_test)


    return train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights, Y_test, len(X.columns)
    #return torch.FloatTensor(X_train), torch.FloatTensor(X_val), torch.FloatTensor(X_test), torch.LongTensor(Y_train), torch.LongTensor(Y_val), torch.LongTensor(Y_test), id_class, len(X.columns), len(id_class)
