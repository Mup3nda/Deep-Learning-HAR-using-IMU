#!/usr/bin/env python3
"""
Predict activity using TensorFlow Lite model

Lightweight version for Raspberry Pi - uses TFLite instead of full TensorFlow.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from data_processing import preprocess_for_prediction
from predictor_tflite import TFLitePredictor

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# Activity emojis
ACTIVITY_EMOJI = {
    "WALKING": "🚶",
    "WALKING_UPSTAIRS": "🔼🚶",
    "WALKING_DOWNSTAIRS": "🔽🚶",
    "SITTING": "🪑",
    "STANDING": "🧍",
    "LAYING": "🛏️"
}

def progress_bar(confidence):
    filled = int(confidence / 5)
    bar = '█'*filled + '░'*(20-filled)
    return f'[{bar}] {confidence:.2f}%'
# ============================================
# Configuration (Edit these)
# ============================================
TFLITE_MODEL = './model/lstm_model_v001_lite.tflite'
CSV_FILE = './data/sensor_data/Recorded/walking2_20260122_191001.csv'



# ============================================
# Main Function
# ============================================
def main():
    logger.info(f" TFLite Prediction")
    print(f"   Model: {TFLITE_MODEL}")
    print(f"   File: {CSV_FILE}")
    
    # Check if files exist
    if not os.path.exists(CSV_FILE):
        logger.error(f" ❌ Error: File not found: {CSV_FILE}")
        return 1
    
    if not os.path.exists(TFLITE_MODEL):
        logger.error(f" ❌ Error: Model not found: {TFLITE_MODEL}")
        return 1
    
    try:
        # Step 1: Preprocess data
        logger.info(f" Preprocessing data...")
        windows = preprocess_for_prediction(CSV_FILE)
        
        # Step 2: Load TFLite model
        logger.info(f" Loading TFLite model...")
        predictor = TFLitePredictor(TFLITE_MODEL)
        
        # Step 3: Make prediction
        logger.info(f" Making prediction...\n")
        result = predictor.predict(windows, verbose=False)
        
        activity = result['activity']
        emoji = ACTIVITY_EMOJI[activity]
        confidence = result['confidence']
        
        print("-"*80)
        print(f"\nActivity: {activity} {emoji} \tModel Confidence: {progress_bar(confidence)} \n")
        print("-"*80)
        # Cleanup
        predictor.close()
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
