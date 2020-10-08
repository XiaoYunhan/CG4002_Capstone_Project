from src.dataset_utils import load_dataset
from src.model_utils import prepare_model 
from src.train import train
from src.test import eval_model

EPOCHS = 300
LEARNING_RATE = 0.0004
BATCH_SIZE = 16

_paths = {
    'headers' : "HAPT Dataset/features.txt",
    'features': "HAPT Dataset/X_full.txt",
    'classes' : "HAPT Dataset/Y_full.txt"
}


if __name__ == "__main__":

    train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights, Y_test, id_class, NUM_FEATURES, NUM_CLASSES = load_dataset(_paths['headers'], _paths['features'], _paths['classes'])
    model = prepare_model('msresnet')
    model, test_loader = train(model, train_dataset, val_dataset, test_dataset, weighted_sampler, class_weights, EPOCHS, BATCH_SIZE, LEARNING_RATE)
    eval_model(model, test_loader, Y_test, id_class)