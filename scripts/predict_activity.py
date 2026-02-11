import sys
import os
#sys.path.insert(0, "../src")
import warnings
import logging
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir, 'src'))

from data_processing import  preprocess_for_prediction
from model_loader import ModelLoader
from predictor import ActivityPredictor

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENAVLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')
logging.getLogger('tenserflow').disabled=True
sys.stderr = open(os.devnull, 'w')


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

CSV_FILE = f'../data/sensor_data/Recorded/standing3_20260122_190409.csv'
MODEL_PATH = f'../model/lstm_model_v001'


def main():
    print(f"\n Starting prediction...")
    print(f"   File: {CSV_FILE}")
    print(f"   Model: {MODEL_PATH}")
    
    # Check if file exists
    if not os.path.exists(CSV_FILE):
        print(f"File do not exist: {CSV_FILE}")
        return None
    
    # Step 1: Preprocess the CSV file
    print(f"\nPreprocessing data...")
    windows = preprocess_for_prediction(CSV_FILE)
    
    # Step 2: Load the model
    print(f"\nLoading model...")
    model = ModelLoader(MODEL_PATH)
    
    # Step 3: Create predictor and make prediction
    print(f"\nMaking prediction...")
    predictor = ActivityPredictor(model)
    result = predictor.predict(windows, verbose=False)
    
    # Step 4: Print simple result
    print(f"\n✅ Result: {result['activity']} ({result['confidence']:.1f}% confidence)\n")
    
    # Step 5: Cleanup
    predictor.close()

if __name__ == "__main__":
    main()