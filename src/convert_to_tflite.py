#!/usr/bin/env python3
"""
Convert TensorFlow LSTM model to TensorFlow Lite

Usage:
    python convert_to_tflite.py
"""

import os
import sys
import numpy as np
import tensorflow.compat.v1 as tf
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from model_loader import ModelLoader

tf.disable_v2_behavior()

# ============================================
# Configuration
# ============================================
MODEL_PATH = 'model/lstm_model_v001'
OUTPUT_PATH = 'model/lstm_model_v001_lite.tflite'
QUANTIZE = False  # Set to True for smaller model (may reduce accuracy slightly)

# ============================================
# Convert to TensorFlow Lite
# ============================================
def convert_to_tflite(sess, input_tensor, output_tensor, output_path, quantize=False):
    """Convert TensorFlow model to TFLite format"""
    logger.info(" 🔄 Converting to TensorFlow Lite...")
    
    # Create converter
    converter = tf.lite.TFLiteConverter.from_session(
        sess,
        [input_tensor],
        [output_tensor]
    )
    
    # Enable optimizations (optional)
    if quantize:
        logger.info("  ⚙️  Applying quantization (reduces model size)...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Convert
    tflite_model = converter.convert()
    
    # Save to file
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    # Get file size
    file_size_kb = os.path.getsize(output_path) / 1024
    
    logger.info(f"✓ Model converted successfully!")
    print(f"  - Output: {output_path}")
    print(f"  - Size: {file_size_kb:.2f} KB")
    
    return tflite_model

# ============================================
# Main Function
# ============================================
def main():
    print("=" * 60)
    print(f"Input model: {MODEL_PATH}")
    print(f"Output file: {OUTPUT_PATH}")
    print(f"Quantization: {'Enabled' if QUANTIZE else 'Disabled'}")
    print("=" * 60)
    
    try:
        # Step 1: Load model using ModelLoader
        logger.info("\n Loading model with ModelLoader...")
        model_loader = ModelLoader(MODEL_PATH)
        
        # Step 2: Restore session
        logger.info("\n Restoring model session...")
        sess = model_loader.restore_session()
        
        # Step 3: Add softmax output for TFLite
        logger.info("\n Adding softmax output layer...")
        output = tf.nn.softmax(model_loader.pred, name='output')
        
        # Step 4: Convert to TFLite
        tflite_model = convert_to_tflite(
            sess, 
            model_loader.x,  # Use input placeholder from ModelLoader
            output,          # Use softmax output
            OUTPUT_PATH, 
            quantize=QUANTIZE
        )
        # Cleanup
        sess.close()
        
        logger.info("✅ Conversion complete!")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())