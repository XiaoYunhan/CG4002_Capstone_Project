from src.dataset_utils import load_dataset
from src.model_utils import prepare_model 
from src.train import train
from src.test import eval_model

EPOCHS = 300
LEARNING_RATE = 0.0004
BATCH_SIZE = 16
NUM_CLASSES = 3


_paths = {
    'headers' : "HAPT Dataset/features.txt",
    'features': "HAPT Dataset/X_full.txt",
    'classes' : "HAPT Dataset/Y_full.txt"
}


if __name__ == "__main__":

    train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights, Y_test, NUM_FEATURES = load_dataset(_paths['headers'], _paths['features'], _paths['classes'])
    model = prepare_model('ffnn')
    model, test_loader = train(model, train_dataset, val_dataset, test_dataset, weighted_sampler, EPOCHS, BATCH_SIZE, LEARNING_RATE)
    eval_model(model, test_loader, Y_test)