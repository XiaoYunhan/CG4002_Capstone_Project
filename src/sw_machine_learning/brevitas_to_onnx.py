import brevitas.onnx as bo
import torch
import os, fnmatch
from os.path import splitext

from src.quantised_models.quant_mlp import *
from src.quantised_models.quant_msresnet import *


converted = []
quantised = []
to_convert = []

onnx = "*.onnx"
pt = "*.pt"

for entry in os.listdir('./onnx'):
    if fnmatch.fnmatch(entry, onnx):
        converted.append(splitext(entry)[0].split("/")[-1])
for entry in os.listdir('./quantised_models'):
    if fnmatch.fnmatch(entry, pt):
        quantised.append(splitext(entry)[0].split("/")[-1])

for file in quantised:
    if file not in converted:
        to_convert.append(file)

for onnx_file in to_convert:
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    if onnx_file.split("_")[0] == "mlp":
        model = quant_mlp()
        input_shape = (1,60)
        model.load_state_dict(torch.load(os.getcwd() + "/quantised_models/" + onnx_file + ".pt", map_location=device))
        bo.export_finn_onnx(model, input_shape, os.getcwd() + "/onnx/" + onnx_file + ".onnx")
    elif onnx_file.split("_")[0] == "msresnet":
        model = quant_msresnet()
        input_shape = (1,1,252)
        model.load_state_dict(torch.load(os.getcwd() + "/quantised_models/" + onnx_file + ".pt", map_location=device))
        bo.export_finn_onnx(model, input_shape, os.getcwd() + "/onnx/" + onnx_file + ".onnx")
