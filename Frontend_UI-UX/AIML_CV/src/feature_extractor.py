class FeatureExtractor:

    def __init__(self):
        pass

    def extract_features(self, hand_landmarks):

        features = []

        # Wrist landmark (landmark 0)
        wrist = hand_landmarks.landmark[0]

        for landmark in hand_landmarks.landmark:

            x = landmark.x - wrist.x
            y = landmark.y - wrist.y
            z = landmark.z - wrist.z

            features.extend([x, y, z])

        return features