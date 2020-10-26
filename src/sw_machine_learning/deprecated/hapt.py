import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

from sklearn.preprocessing import MinMaxScaler    
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

## Loading Raw Data / Features

headers = pd.read_csv("HAPT Dataset/features.txt")

X = pd.read_csv("HAPT Dataset/X_full.txt", sep='\s+')
Y = pd.read_csv("HAPT Dataset/Y_full.txt", names=["Activity"])

# Map enumerated classes to start from 0

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

# Split into trainval and test
#Stratified split allows us to make sure there is good spread of classes across 3 sets
X_trainval, X_test, Y_trainval, Y_test = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=69)

# Split trainval into train and val
X_train, X_val, Y_train, Y_val = train_test_split(X_trainval, Y_trainval, test_size=0.1, stratify=Y_trainval, random_state=21)


## Normalise data to scale between 0 and 1
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)
X_train, Y_train = np.array(X_train), np.array(Y_train)
X_val, Y_val = np.array(X_val), np.array(Y_val)
X_test, Y_test = np.array(X_test), np.array(Y_test)


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

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(25,7))
# Train
sns.barplot(data = pd.DataFrame.from_dict([get_class_distribution(Y_train)]).melt(), x = "variable", y="value", hue="variable",  ax=axes[0]).set_title('Class Distribution in Train Set')
# Validation
sns.barplot(data = pd.DataFrame.from_dict([get_class_distribution(Y_val)]).melt(), x = "variable", y="value", hue="variable",  ax=axes[1]).set_title('Class Distribution in Val Set')
# Test
sns.barplot(data = pd.DataFrame.from_dict([get_class_distribution(Y_test)]).melt(), x = "variable", y="value", hue="variable",  ax=axes[2]).set_title('Class Distribution in Test Set')

#plt.savefig("plot.png")

## Form DataFrames - converting numpy arrays into tensors
class ClassifierDataset(Dataset):
    
    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data
        
    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]
        
    def __len__ (self):
        return len(self.X_data)


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

## Setting General Model Params
MODEL = "CNN"
EPOCHS = 300
BATCH_SIZE = 16
LEARNING_RATE = 0.0004
WEIGHT_DECAY = 0.001
NUM_FEATURES = len(X.columns)
NUM_CLASSES = 12

## Loading Data
train_loader = DataLoader(dataset=train_dataset,
                          batch_size=BATCH_SIZE,
                          sampler=weighted_sampler
)
val_loader = DataLoader(dataset=val_dataset, batch_size=1)
test_loader = DataLoader(dataset=test_dataset, batch_size=1)

## 3-layer FFNN (Baseline NN)
class MulticlassFFNN(nn.Module):
    def __init__(self, num_feature, num_class):
        super(MulticlassFFNN, self).__init__()
        
        self.layer_1 = nn.Linear(num_feature, 512)
        self.layer_2 = nn.Linear(512, 128)
        self.layer_3 = nn.Linear(128, 64)
        self.layer_out = nn.Linear(64, num_class) 
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.2)
        self.batchnorm1 = nn.BatchNorm1d(512)
        self.batchnorm2 = nn.BatchNorm1d(128)
        self.batchnorm3 = nn.BatchNorm1d(64)
        
    def forward(self, x):
        x = self.layer_1(x)
        x = self.batchnorm1(x)
        x = self.relu(x)
        
        x = self.layer_2(x)
        x = self.batchnorm2(x)
        x = self.relu(x)
        x = self.dropout(x)
        
        x = self.layer_3(x)
        x = self.batchnorm3(x)
        x = self.relu(x)
        x = self.dropout(x)
        
        x = self.layer_out(x)
        
        return x

## Initialise 3-Layer FFNN
model_ffnn = MulticlassFFNN(num_feature = NUM_FEATURES, num_class=NUM_CLASSES)
model_ffnn.to("cpu")

criterion = nn.CrossEntropyLoss(weight=class_weights.to("cpu"))
optimizer = optim.Adam(model_ffnn.parameters(), lr=LEARNING_RATE)
##print(model_ffnn)


## CNN
class convNet(nn.Module):
    def __init__(self):
        super(nn.Net, self).__init__()
        
        # Declare all the layers for feature extraction
        self.features = nn.Sequential(nn.Conv1d(in_channels=NUM_FEATURES,
                                                out_channels=NUM_FEATURES,
                                                kernel_size=3,
                                                stride=1,
                                                padding=1), 
                                        nn.ReLU(inplace=True),

                                        nn.Conv2d(in_channels=NUM_FEATURES,
                                                out_channels=256,
                                                kernel_size=3,
                                                stride=1,
                                                padding=1), 
                                        nn.MaxPool2d(2, 2),
                                        nn.ReLU(inplace=True),
                                        nn.BatchNorm1d(10),

                                        nn.Conv1d(in_channels=256,
                                                out_channels=128,
                                                kernel_size=3,
                                                stride=1,
                                                padding=1),
                                        nn.ReLU(inplace=True),
                                        nn.BatchNorm1d(20),

                                        nn.Conv1d(in_channels=128,
                                                out_channels=64,
                                                kernel_size=3,
                                                stride=1,
                                                padding=1),
                                        nn.MaxPool1d(2, 2),
                                        nn.ReLU(inplace=True),
                                        nn.BatchNorm1d(40))
        
        # Declare all the layers for classification
        self.classifier = nn.Sequential(
            nn.Linear(NUM_FEATURES * 0.25 * 40, 200),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(200, 500),
            nn.ReLU(inplace=True),
            nn.Linear(500, NUM_CLASSES))
        
    def forward(self, x):
      
        # Apply the feature extractor in the input
        x = self.features(x)
        print(x.shape)
        exit()
        # Squeeze the three spatial dimensions in one
        x = x.view(-1, NUM_FEATURES * 0.25 * 40)
        
        # Classify the images
        x = self.classifier(x)
        return x

## Initialise CNN
model_cnn = MulticlassFFNN(num_feature = NUM_FEATURES, num_class=NUM_CLASSES)
model_cnn.to("cpu")

criterion = nn.CrossEntropyLoss(weight=class_weights.to("cpu"))
optimizer = optim.Adam(model_cnn.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
##print(model_ffnn)


## Train model

#Calculate accuracy for validation
def multi_acc(Y_pred, Y_test):
    Y_pred_softmax = torch.log_softmax(Y_pred, dim = 1)
    _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)    
    
    correct_pred = (Y_pred_tags == Y_test).float()
    acc = correct_pred.sum() / len(correct_pred)
    
    acc = torch.round(acc) * 100
    
    return acc

#Store Statisitcs
accuracy_stats = {
    'train': [],
    "val": []
}

loss_stats = {
    'train': [],
    "val": []
}

print("Begin training.")
for e in tqdm(range(1, EPOCHS+1)):
    if MODEL == "FFNN":
        model = model_ffnn
    elif MODEL == "CNN":
        model = model_cnn

    # TRAINING
    train_epoch_loss = 0
    train_epoch_acc = 0
    model.train()
    for X_train_batch, Y_train_batch in train_loader:
        X_train_batch, Y_train_batch = X_train_batch.to("cpu"), Y_train_batch.to("cpu")
        optimizer.zero_grad()
        
        Y_train_pred = model(X_train_batch)
        Y_train_batch = Y_train_batch.view(-1)
        #Y_train_pred = Y_train_pred.view(Y_train_batch.size(0), -1)
        train_loss = criterion(Y_train_pred, Y_train_batch)
        train_acc = multi_acc(Y_train_pred, Y_train_batch)
        
        train_loss.backward()
        optimizer.step()
        
        train_epoch_loss += train_loss.item()
        train_epoch_acc += train_acc.item()
        
        
    # VALIDATION    
    with torch.no_grad():
        
        val_epoch_loss = 0
        val_epoch_acc = 0
        
        model.eval()
        for X_val_batch, Y_val_batch in val_loader:
            X_val_batch, Y_val_batch = X_val_batch.to("cpu"), Y_val_batch.to("cpu")
            
            Y_val_pred = model(X_val_batch)
            Y_val_batch = Y_val_batch.view(-1) 
            val_loss = criterion(Y_val_pred, Y_val_batch)
            val_acc = multi_acc(Y_val_pred, Y_val_batch)
            
            val_epoch_loss += val_loss.item()
            val_epoch_acc += val_acc.item()
    loss_stats['train'].append(train_epoch_loss/len(train_loader))
    loss_stats['val'].append(val_epoch_loss/len(val_loader))
    accuracy_stats['train'].append(train_epoch_acc/len(train_loader))
    accuracy_stats['val'].append(val_epoch_acc/len(val_loader))
                              
    
    print(f'Epoch {e+0:03}: | Train Loss: {train_epoch_loss/len(train_loader):.5f} | Val Loss: {val_epoch_loss/len(val_loader):.5f} | Train Acc: {train_epoch_acc/len(train_loader):.3f}| Val Acc: {val_epoch_acc/len(val_loader):.3f}')

## Visualisation of Training

# Create dataframes
train_val_acc_df = pd.DataFrame.from_dict(accuracy_stats).reset_index().melt(id_vars=['index']).rename(columns={"index":"epochs"})
train_val_loss_df = pd.DataFrame.from_dict(loss_stats).reset_index().melt(id_vars=['index']).rename(columns={"index":"epochs"})
# Plot the dataframes
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20,7))
sns.lineplot(data=train_val_acc_df, x = "epochs", y="value", hue="variable",  ax=axes[0]).set_title('Train-Val Accuracy/Epoch')
sns.lineplot(data=train_val_loss_df, x = "epochs", y="value", hue="variable", ax=axes[1]).set_title('Train-Val Loss/Epoch')

## Evaluation

Y_pred_list = []
with torch.no_grad():
    model.eval()
    for X_batch, _ in test_loader:
        X_batch = X_batch.to("cpu")
        Y_test_pred = model(X_batch)
        Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
        _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
        Y_pred_list.append(Y_pred_tags.cpu().numpy())

# Flatten to input to confusion matrix        
Y_pred_list = [a.squeeze().tolist() for a in Y_pred_list]

## Confusion Matrix
confusion_matrix_df = pd.DataFrame(confusion_matrix(Y_test, Y_pred_list)).rename(columns=id_class, index=id_class)
sns.heatmap(confusion_matrix_df, annot=True)
plt.savefig("confusion_3_CNN.png")

## Classification Report
print(classification_report(Y_test, Y_pred_list))