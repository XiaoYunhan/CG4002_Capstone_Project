import os
import torch
import torch.nn as nn

## 3-layer FFNN (Baseline NN)
class MulticlassFFNN(nn.Module):
    def __init__(self, num_feature, num_class):
        super(MulticlassFFNN, self).__init__()
        
        self.layer_1 = nn.Linear(num_feature, 128)
        self.layer_2 = nn.Linear(128, 64)
        self.layer_3 = nn.Linear(64, 32)
        self.layer_out = nn.Linear(32, num_class) 
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.2)
        self.batchnorm1 = nn.BatchNorm1d(128)
        self.batchnorm2 = nn.BatchNorm1d(64)
        self.batchnorm3 = nn.BatchNorm1d(32)
        
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
def mlp_reduced(**kwargs):
    model_ffnn = MulticlassFFNN(num_feature=60, num_class=3)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model_ffnn.to(device)
    return model_ffnn
