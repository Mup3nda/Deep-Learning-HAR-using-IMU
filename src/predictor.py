import numpy as np
from collections import Counter
import tensorflow.compat.v1 as tf

# #--------------------------------
# # Remove this
# # Cell 1: Imports
# from src.data_preprocessing import preprocess_for_prediction
# from src.model_loader import ModelLoader
# from src.predictor import ActivityPredictor

# model = ModelLoader('model/lstm_model_v002')
# #--------------------------------

LABELS = [
    "WALKING",
    "WALKING_UPSTAIRS", 
    "WALKING_DOWNSTAIRS",
    "SITTING",
    "STANDING",
    "LAYING"
]

class ActivityPredictor:
    def __init__(self, model):
        self.model = model
        self.session = None

    def predict(self, windows, verbos=True):

        if self.session is None:
            self.session = self.model.restore_session()

        predictions_raw = self.session.run(
            self.model.pred, feed_dict={self.model.x: windows}
        )
        probrabilities = self.session.run(
            tf.nn.softmax(predictions_raw)
        )
        predicted_class = predictions_raw.argmax(axis=1)

        vote_counts = Counter(predicted_class)
        most_common_class = vote_counts.most_common(1)[0][0]
        # vote_count = vote_counts.most_common(1)[0][1]

        confidence = [probrabilities[i][predicted_class[i]] 
                      for i in range(len(windows))]
        avg_confidence = np.mean(confidence) * 100

        results = {
            'activity': LABELS[most_common_class],
            'confidence': avg_confidence,
            'vote_counts': vote_counts,
            'probabilities': probrabilities
        }
        if verbos:
            self._print_results(results, len(windows))
        
        return results
    
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
            print(f"\t{LABELS[cls]:20s}: {count:3d} ({pct:.1f}%)")
        print(f"{'='*50}\n")

    def close(self):
        if self.session:
            self.session.close()