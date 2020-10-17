import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from tqdm import tqdm
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
import os
import datetime

def load_trainval(train_dataset, val_dataset, test_dataset, weighted_sampler, BATCH_SIZE=16):
    train_loader = DataLoader(dataset=train_dataset,
                            batch_size=BATCH_SIZE,
                            sampler=weighted_sampler,
                            num_workers=8
    )
    val_loader = DataLoader(dataset=val_dataset, batch_size=1)
    test_loader = DataLoader(dataset=test_dataset, batch_size=1)

    return train_loader, val_loader, test_loader
# def seq_loader(X_data, Y_data, window):
#     out = []
#     for i in range(0, len(X_data) - window, window):
#         seq = X_data[i:i+window]
#         label = Y_data[i]
#         out.append((seq, label))
#     return out
        
# def load_trainval(X_train, X_val, X_test, Y_train, Y_val, Y_test, BATCH_SIZE=16):
#     train_loader = seq_loader(X_train, Y_train, 64)
#     val_loader = seq_loader(X_val, Y_val, 64)
#     test_loader = seq_loader(X_test, Y_test, 64)

#     return train_loader, val_loader, test_loader


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

def train_model(model, train_loader, val_loader, EPOCHS=300, LEARNING_RATE=0.0004):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print("Begin training.")
    for e in tqdm(range(1, EPOCHS+1)):
        best_model_wts = copy.deepcopy(model.state_dict())
        best_acc = 0.0

        # TRAINING
        train_epoch_loss = 0.0
        train_epoch_acc = 0.0
        model.train()
        for X_train_batch, Y_train_batch in train_loader:
            X_train_batch, Y_train_batch = X_train_batch.to(device), Y_train_batch.to(device)
            optimizer.zero_grad()
            Y_train_pred = model(X_train_batch)
            Y_train_batch = Y_train_batch.view(-1)
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
                X_val_batch, Y_val_batch = X_val_batch.to(device), Y_val_batch.to(device)
                
                Y_val_pred = model(X_val_batch)
                Y_val_batch = Y_val_batch.view(-1) 
                val_loss = criterion(Y_val_pred, Y_val_batch)
                val_acc = multi_acc(Y_val_pred, Y_val_batch)
                
                val_epoch_loss += val_loss.item()
                val_epoch_acc += val_acc.item()
                if val_epoch_acc > best_acc:
                    best_acc = val_epoch_acc
                    best_model_wts = copy.deepcopy(model.state_dict())
        loss_stats['train'].append(train_epoch_loss/len(train_loader))
        loss_stats['val'].append(val_epoch_loss/len(val_loader))
        accuracy_stats['train'].append(train_epoch_acc/len(train_loader))
        accuracy_stats['val'].append(val_epoch_acc/len(val_loader))
                                
        
        print(f'Epoch {e+0:03}: | Train Loss: {train_epoch_loss/len(train_loader):.5f} | Val Loss: {val_epoch_loss/len(val_loader):.5f} | Train Acc: {train_epoch_acc/len(train_loader):.3f}| Val Acc: {val_epoch_acc/len(val_loader):.3f}')
    cwd = os.getcwd()
    x = datetime.datetime.now()
    PATH = cwd + "/quantised_models/ffnn" + x.strftime("_%d%m_%H%M") +".pt"
    model.load_state_dict(best_model_wts)
    torch.save(model.state_dict(), PATH)
    return model

def visual_train():
    ## Visualisation of Training

    # Create dataframes
    train_val_acc_df = pd.DataFrame.from_dict(accuracy_stats).reset_index().melt(id_vars=['index']).rename(columns={"index":"epochs"})
    train_val_loss_df = pd.DataFrame.from_dict(loss_stats).reset_index().melt(id_vars=['index']).rename(columns={"index":"epochs"})
    # Plot the dataframes
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20,7))
    sns.lineplot(data=train_val_acc_df, x = "epochs", y="value", hue="variable",  ax=axes[0]).set_title('Train-Val Accuracy/Epoch')
    sns.lineplot(data=train_val_loss_df, x = "epochs", y="value", hue="variable", ax=axes[1]).set_title('Train-Val Loss/Epoch')

def train(model, train_dataset, val_dataset, test_dataset, weighted_sampler, EPOCHS, BATCH_SIZE, LEARNING_RATE):
    train_loader, val_loader, test_loader = load_trainval(train_dataset, val_dataset, test_dataset, weighted_sampler, BATCH_SIZE)
    model = train_model(model, train_loader, val_loader, EPOCHS, LEARNING_RATE)
    visual_train()
    
    return model, test_loader