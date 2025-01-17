import os

from src.dataset_utils import load_dataset
from src.model_utils import prepare_model 
from src.train import train
from src.test import eval_model

EPOCHS = 50
LEARNING_RATE = 0.0004
BATCH_SIZE = 64
NUM_CLASSES = 3
DATA_LEN = 64

model_name = 'quant_mlp_feat'

_paths = {
    'compiled'          : os.getcwd() + "/../../data/Raw Data/moves/compiled.txt",
    'compiled_fpga'     : os.getcwd() + "/../../data/Raw Data/moves/compiled_int.txt",
    'features'          : os.getcwd() + "/../../data/Raw Data/moves/features.txt",
    'features_fpga'     : os.getcwd() + "/../../data/Raw Data/moves/features_int.txt",
    'compiled_cnn'      : os.getcwd() + "/../../data/Raw Data/compiled_cnn.txt",
    'compiled_hapt'     : os.getcwd() + "/../../data/HAPT Dataset/RawData/compiled_hapt.txt",
    'model_save'        : os.getcwd() + "/models/" + model_name,
    'quant_model_save'  : os.getcwd() + "/quantised_models/" + model_name
}


if __name__ == "__main__":

    train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights, Y_test, NUM_FEATURES = load_dataset(_paths['features_fpga'], DATA_LEN)
    model = prepare_model(model_name)
    model, test_loader = train(model, train_dataset, val_dataset, test_dataset, weighted_sampler, EPOCHS, BATCH_SIZE, LEARNING_RATE, _paths['quant_model_save'])
    eval_model(model, test_loader, Y_test)
