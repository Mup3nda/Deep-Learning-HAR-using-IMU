import numpy as np
import tensorflow.compat.v1 as tf
from collections import Counter

LABELS = [
    "WALKING",
    "WALKING_UPSTAIRS", 
    "WALKING_DOWNSTAIRS",
    "SITTING",
    "STANDING",
    "LAYING"
]

class ActivityPredictor:
    """Predict activities from sensor data"""
    
    def __init__(self, model_loader):
        self.model = model_loader
        self.session = None
    
    def predict(self, windows, verbose=True):
        """
        Predict activity from preprocessed windows
        
        Args:
            windows: np.array of shape (n_windows, 128, 9)
            verbose: Print detailed results
        
        Returns:
            dict: {
                'activity': str,
                'confidence': float,
                'vote_counts': dict,
                'probabilities': np.array
            }
        """
        if self.session is None:
            self.session = self.model.restore_session()
        
        # Get predictions
        predictions_raw = self.session.run(
            self.model.pred, 
            feed_dict={self.model.x: windows}
        )
        probabilities = self.session.run(
            tf.nn.softmax(predictions_raw)
        )
        predicted_classes = predictions_raw.argmax(axis=1)
        
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
        """Close TensorFlow session"""
        if self.session:
            self.session.close()