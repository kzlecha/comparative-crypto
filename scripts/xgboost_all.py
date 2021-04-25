"""https://xgboost.readthedocs.io/en/latest/python/python_intro.html"""


import numpy as np
import xgboost as xgb

from pandas import read_csv, DataFrame

from matplotlib import pyplot as pyp
from sklearn.model_selection import train_test_split

dir_path = "data/2h/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]


accuracies = {}

for filename in file_list:
    crypto_name = filename.replace("2h.csv","")
    data = read_csv(dir_path+filename)
    
    X_train, X_test, y_train, y_test = train_test_split(
        data[:, :-1], data[:,-1], test_size=0.30,
        )
    
    model = xgb.XGBClassifier(
        n_estimators=10000,
        max_depth=15,
        learning_rate=0.1,
        objective="binary:logistic",
        num_class=2,
        verbosity=2
    )

    model.fit(trainX,trainY)
    predictions = model.predict(testX)

    accuracies[crypto_name] = (predictions == y_test).mean()

    model.save_model("models/2h/"+crypto_name+".model")

DataFrame(accuracies).to_csv("xgboost_accuracy.csv", index=False)