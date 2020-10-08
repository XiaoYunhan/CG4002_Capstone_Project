import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from tqdm import tqdm
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_trainval(train_dataset, val_dataset, test_dataset, weighted_sampler, BATCH_SIZE=16):
    train_loader = DataLoader(dataset=train_dataset,
                            batch_size=BATCH_SIZE,
                            sampler=weighted_sampler
    )
    val_loader = DataLoader(dataset=val_dataset, batch_size=1)
    test_loader = DataLoader(dataset=test_dataset, batch_size=1)

    return train_loader, val_loader, test_loader

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

def train_model(model, train_loader, val_loader, class_weights, EPOCHS=300, LEARNING_RATE=0.0004):
    criterion = nn.CrossEntropyLoss(weight=class_weights.to("cpu"))
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    print("Begin training.")
    for e in tqdm(range(1, EPOCHS+1)):

        # TRAINING
        train_epoch_loss = 0
        train_epoch_acc = 0
        model.train()
        for X_train_batch, Y_train_batch in train_loader:
            X_train_batch, Y_train_batch = X_train_batch.to("cpu"), Y_train_batch.to("cpu")
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

def train(model, train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights, EPOCHS, BATCH_SIZE, LEARNING_RATE):
    train_loader, val_loader, test_loader = load_trainval(train_dataset, val_dataset, test_dataset, weighted_sampler, BATCH_SIZE)
    model = train_model(model, train_loader, val_loader, class_weights, EPOCHS, LEARNING_RATE)
    visual_train()
    
    return model, test_loader