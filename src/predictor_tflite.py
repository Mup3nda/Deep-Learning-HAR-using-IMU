
import numpy as np
try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite
import logging

from collections import Counter

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

LABELS = [
    "WALKING",
    "WALKING_UPSTAIRS", 
    "WALKING_DOWNSTAIRS",
    "SITTING",
    "STANDING",
    "LAYING"
]

class TFLitePredictor:
    """Predict activities using TensorFlow Lite model"""

    
    
    def __init__(self, model_path):
        """
        Initialize TFLite predictor
        
        Args:
            model_path: Path to .tflite model file
        """
        self.model_path = model_path
        
        # Load TFLite model
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Get model info
        self.input_shape = self.input_details[0]['shape']
        self.output_shape = self.output_details[0]['shape']
        
        logger.info(f"✓ TFLite model loaded: {model_path}")
        logger.info(f"  Input shape: {self.input_shape}")
        logger.info(f"  Output shape: {self.output_shape}")
    
    def predict_single(self, window):
        """
        Predict activity for a single window
        
        Args:
            window: np.array of shape (128, 9)
        
        Returns:
            np.array: Probabilities for each class
        """
        # Reshape to match model input (add batch dimension)
        input_data = np.expand_dims(window, axis=0).astype(np.float32)
        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        # Run inference
        self.interpreter.invoke()
        # Get output tensor
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        return output_data[0]  # Return probabilities
    
    def predict(self, windows, verbose=True):
        """
        Predict activity from preprocessed windows
        """
        # Predict for each window
        all_probabilities = []
        predicted_classes = []
        
        for i, window in enumerate(windows):
            probs = self.predict_single(window)
            all_probabilities.append(probs)
            predicted_classes.append(probs.argmax())
        
        probabilities = np.array(all_probabilities)
        
        # Voting
        vote_counts = Counter(predicted_classes)
        most_common_class = vote_counts.most_common(1)[0][0]
        
        # Confidence
        confidences = [probabilities[i][predicted_classes[i]] 
                      for i in range(len(windows))]
        avg_confidence = np.mean(confidences) * 100
        
        result = {
            'activity': LABELS[most_common_class],
            'confidence': avg_confidence,
            'vote_counts': vote_counts,
            'probabilities': probabilities
        }
        
        if verbose:
            self._print_results(result, len(windows))
        
        return result
    
    def _print_results(self, result, total_windows):
        """Print formatted prediction results"""
        print(f"\n{'='*50}")
        print(f"PREDICTION RESULTS")
        print(f"{'='*50}")
        print(f"\n  Activity: {result['activity']}")
        print(f"  Confidence: {result['confidence']:.1f}%")
        print(f"\n  Vote breakdown:")
        for cls, count in result['vote_counts'].most_common():
            pct = count / total_windows * 100
            print(f"    {LABELS[cls]:20s}: {count:3d} ({pct:.1f}%)")
        print(f"{'='*50}\n")
    
    def close(self):
        pass
