import torch
import torch.nn as nn

from .mobilenet import *
from .msresnet import *
from .mlp import *
    
_models = {
    'msresnet' : msresnet,
    'ffnn' : ffnn,
    'mobilenetv3_small_w7d20': mobilenetv3_small_w7d20,
    'mobilenetv3_small_wd2': mobilenetv3_small_wd2,
    'mobilenetv3_small_w3d4': mobilenetv3_small_w3d4,
    'mobilenetv3_small_w1': mobilenetv3_small_w1,
    'mobilenetv3_small_w5d4': mobilenetv3_small_w5d4,
    'mobilenetv3_large_w7d20': mobilenetv3_large_w7d20,
    'mobilenetv3_large_wd2': mobilenetv3_large_wd2,
    'mobilenetv3_large_w3d4': mobilenetv3_large_w3d4,
    'mobilenetv3_large_w1': mobilenetv3_large_w1,
    'mobilenetv3_large_w5d4': mobilenetv3_large_w5d4,
}

def get_model(name, **kwargs):
    name = name.lower()
    if name not in _models:
        raise ValueError("Unsupported model: {}".format(name))
    net = _models[name](**kwargs)
    return net

def prepare_model(model_name,
                  use_pretrained=False,
                  pretrained_model_file_path=None,
                  use_cuda=False,
                  use_data_parallel=True,
                  net_extra_kwargs=None,
                  load_ignore_extra=False,
                  num_classes=None,
                  in_channels=None,
                  remap_to_cpu=False,
                  remove_module=False):
 
    kwargs = {"pretrained": use_pretrained}
    if num_classes is not None:
        kwargs["num_classes"] = num_classes
    if in_channels is not None:
        kwargs["in_channels"] = in_channels
    if net_extra_kwargs is not None:
        kwargs.update(net_extra_kwargs)

    net = get_model(model_name, **kwargs)

    if use_data_parallel and use_cuda:
        net = torch.nn.DataParallel(net)

    if use_cuda:
        net = net.cuda()

    return net