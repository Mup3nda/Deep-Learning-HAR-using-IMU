import sys
import os

sys.path.insert(0, "../src")

from data_processing import  preprocess_for_prediction
from model_loader import ModelLoader


model = ModelLoader('../model/lstm_model_v001')

predictor = ActivityPredictor(model)

csv_file = '../data/sensor_data/Recorded/walking2_20260122_191001.csv'

windows = preprocess_for_prediction(csv_file)

result = predictor.predict(windows)

predictor.close()