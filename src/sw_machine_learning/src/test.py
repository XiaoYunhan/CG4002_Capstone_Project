import torch

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report

def eval_model(model, test_loader, Y_test):
    Y_pred_list = []
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        model.eval()
        for X_batch, _ in test_loader:
            X_batch = X_batch.to(device)
            #X_batch = X_batch.unsqueeze(0)
            #Y_test_pred = model(X_batch).unsqueeze(0)
            Y_test_pred = model(X_batch)
            Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
            _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
            Y_pred_list.append(Y_pred_tags.cpu().numpy())

    # Flatten to input to confusion matrix        
    Y_pred_list = [a.squeeze().tolist() for a in Y_pred_list]

    ## Confusion Matrix
    confusion_matrix_df = pd.DataFrame(confusion_matrix(Y_test, Y_pred_list))
    sns.heatmap(confusion_matrix_df, annot=True)
    plt.savefig("msresnet_init.png")

    ## Classification Report
    print(classification_report(Y_test, Y_pred_list))