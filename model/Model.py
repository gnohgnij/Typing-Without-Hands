import numpy as np
import joblib
import math

class Model:
    def __init__(self):
        self.predictor = joblib.load("./model/predictor.pkl")[0]

    def predict(self, x, y):
        '''
        Predicts the x and y coordinates of the mouse cursor
        '''
        coor = np.array([(x, y)])
        pred = self.predictor.predict(coor)[0]
        x_pred = pred[0]
        y_pred = pred[1]
        return int(x_pred), int(y_pred)