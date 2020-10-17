import os

from src.dataset_utils import load_dataset
from src.model_utils import prepare_model 
from src.train import train
from src.test import eval_model

EPOCHS = 100
LEARNING_RATE = 0.0007
BATCH_SIZE = 128
NUM_CLASSES = 3

_paths = {
    'compiled' : os.getcwd() + "/../../data/Raw Data/compiled.txt"
}


if __name__ == "__main__":

    train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights, Y_test, NUM_FEATURES = load_dataset(_paths['compiled'])
    model = prepare_model('quant_mlp')
    model, test_loader = train(model, train_dataset, val_dataset, test_dataset, weighted_sampler, EPOCHS, BATCH_SIZE, LEARNING_RATE)
    eval_model(model, test_loader, Y_test)