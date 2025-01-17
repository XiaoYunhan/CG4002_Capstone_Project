import os
import torch.nn as nn
import brevitas.nn as qnn
from brevitas.core.quant import QuantType

## 3-layer FFNN (Baseline NN)
class QuantMLP(nn.Module):
    def __init__(self, num_feature, num_class):
        super(QuantMLP, self).__init__()
        self.layer_1 = qnn.QuantLinear(num_feature, 128, bias=False, weight_quant_type=QuantType.INT, weight_bit_width=8)
        self.layer_2 = qnn.QuantLinear(128, 64, bias=False, weight_quant_type=QuantType.INT, weight_bit_width=4)
        self.layer_3 = qnn.QuantLinear(64, 32, bias=False, weight_quant_type=QuantType.INT, weight_bit_width=4)
        self.layer_out = qnn.QuantLinear(32, num_class, bias=False, weight_quant_type=QuantType.INT, weight_bit_width=4)
        
        self.relu = qnn.QuantReLU(quant_type=QuantType.INT, bit_width=4, max_val=6)
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
def quant_mlp_feat(**kwargs):
    model_ffnn = QuantMLP(num_feature=64, num_class=3)
    model_ffnn.to("cpu")
    return model_ffnn
