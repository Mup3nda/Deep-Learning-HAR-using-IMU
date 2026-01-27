"""
Simple script to predict activity from a single CSV file

How it works:
1. Loads a CSV file with sensor data
2. Preprocesses the data into windows
3. Loads the trained model
4. Predicts the activity
5. Prints the result

Usage:
    python predict_single.py
    (Edit the CSV_FILE and MODEL_PATH variables below)
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from data_processing import preprocess_for_prediction
from model_loader import ModelLoader
from predictor import ActivityPredictor

# ===========================================
# EDIT THESE VARIABLES
# ===========================================
CSV_FILE = '../data/sensor_data/Recorded/walking2_20260122_191001.csv'
MODEL_PATH = '../model/lstm_model_v002'
# ===========================================

def main():
    print(f"\n🚀 Starting prediction...")
    print(f"   File: {CSV_FILE}")
    print(f"   Model: {MODEL_PATH}")
    
    # Check if file exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: File not found: {CSV_FILE}")
        return
    
    # Step 1: Preprocess the CSV file
    print(f"\n📊 Preprocessing data...")
    windows = preprocess_for_prediction(CSV_FILE)
    
    # Step 2: Load the model
    print(f"\n🤖 Loading model...")
    model = ModelLoader(MODEL_PATH)
    
    # Step 3: Create predictor and make prediction
    print(f"\n🔮 Making prediction...")
    predictor = ActivityPredictor(model)
    result = predictor.predict(windows, verbos=True)
    
    # Step 4: Print simple result
    print(f"\n✅ Result: {result['activity']} ({result['confidence']:.1f}% confidence)\n")
    
    # Step 5: Cleanup
    predictor.close()

if __name__ == "__main__":
    main()