#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from finn.transformation.fpgadataflow.make_deployment import DeployToPYNQ

# FINN will use ssh to deploy and run the generated accelerator
ip = os.getenv("pynq", "137.132.86.230")
username = os.getenv("PYNQ_USERNAME", "xilinx")
password = os.getenv("PYNQ_PASSWORD", "xilinx")
port = os.getenv("PYNQ_PORT", 22)
target_dir = os.getenv("PYNQ_TARGET_DIR", "/home/xilinx/finn_cnv")

model = ModelWrapper(build_dir + "/cnv_synth.onnx")
model = model.transform(DeployToPYNQ(ip, port, username, password, target_dir))
model.save(build_dir + "/cnv_deploy.onnx")

