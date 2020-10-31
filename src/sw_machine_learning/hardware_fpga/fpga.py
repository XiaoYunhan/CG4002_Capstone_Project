from driver import FINNAccelDriver
import numpy as np

class MyFinnDriver():
    def __init__(self):
        #FINN Driver arguments
        N = 1
        bitfile = "resizer.bit"
        platform = "zynq-iodma"
        #Instantiate FINN accelerator
        self.driver = FINNAccelDriver(N, bitfile, platform)
        
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
        self.driver.copy_output_data_to_device(obuf_packed)
        obuf_folded = self.driver.fold_input(obuf_packed)
        obuf_normal = self.driver.fold_input(obuf_folded)
        return obuf_normal #output file
    
    
if __name__ == "__main__": 
    finnDriver = MyFinnDriver()

    input = np.random.uniform(0,1,(1,60))
    #print(input.shape)
        
    output = finnDriver.execute(input)
    
    #print(output)

