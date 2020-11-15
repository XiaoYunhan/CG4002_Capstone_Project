from driver import FINNAccelDriver
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from joblib import load
import os

class FinnDriver():
    def __init__(self):
        #FINN Driver arguments
        N = 1
        bitfile = "resizer.bit"
        platform = "zynq-iodma"
        #Instantiate FINN accelerator
        self.driver = FINNAccelDriver(N, bitfile, platform)
        self.scaler = load(os.getcwd() + '/models/feat_all_scaler.joblib')
        
    def execute(self, input_data):
        #load data as input to model
        ibuf_normal = input_data
        ibuf_folded = self.driver.fold_input(ibuf_normal)
        ibuf_packed = self.driver.fold_input(ibuf_folded)
        self.driver.copy_input_data_to_device(ibuf_packed)
        
        #execute accelerator
        self.driver.execute()
        
        #unpack, unfold and return output
        obuf_packed = np.empty_like(self.driver.obuf_packed_device)
        self.driver.copy_output_data_from_device(obuf_packed)
        obuf_folded = self.driver.unpack_output(obuf_packed)
        obuf_normal = self.driver.unfold_output(obuf_folded)
        return obuf_normal #output file
    
    def predict(self, input): 
        #print(input.shape)
        input = self.scaler.transform(input)
        output = self.execute(input.astype(np.uint8)[0])
        output = np.exp(output - np.max(output))
        output = output / output.sum()
        output = np.argmax(output)
        
        return output

if __name__ == "__main__":
    input = np.random.uniform(0, 1, (1, 72))
    print(FinnDriver().predict(input))