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
    #input = i[0]
    
    t = np.array([[2.374, 1.2977, 2.0687, 0.9241, -0.0779, 0.4592, 2.6489, 1.6794, 2.1221, 0.9192, -0.0837, 0.4597, 1.6336, 1.6412, 2.5191, 0.9221, -0.0767, 0.4534, -0.916, 1.2519, 0.7863, 0.9277, -0.0779, 0.4563, 3.8092, 1.3817, 1.8779, 0.9187, -0.0823, 0.4551, 3.0153, 1.0687, 2.2137, 0.9224, -0.0796, 0.4546, 1.3359, 1.8397, 1.7481, 0.9202, -0.0693, 0.4624, 9.7634, 4.5267, 6.9924, 1.075, -0.073, 0.5901, 60.6641, 85.4886, 113.9237, 1.1702, -0.262, 0.8623, 55.6794, 172.7252, 165.7633, 1.0286, -0.3799, 1.0869]])
    
    with open('input.npy', 'wb') as f:
        np.save(f, np.array(t))   

    input = np.load('input.npy')
    print(input.shape)
        
    output = finnDriver.execute(input)
    
    print(output)

