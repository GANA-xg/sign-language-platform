class FeatureExtractor:

    def __init__(self):
        pass

    def extract_features(self, hand_landmarks):
        """
        Extract 63 landmark features exactly the same way
        as used during training.
        """

        features = []

        for landmark in hand_landmarks.landmark:

            features.extend([
                landmark.x,
                landmark.y,
                landmark.z
            ])

        return features