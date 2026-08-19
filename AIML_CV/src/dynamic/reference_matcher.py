import os
import glob
import numpy as np


class ReferenceMatcher:

    def __init__(self):

        print()
        print("========================================")
        print("LOADING REFERENCE SEQUENCES")
        print("========================================")

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.reference_dir = os.path.join(
            base_dir,
            "..",
            "..",
            "processed",
            "dynamic_sequences"
        )

        self.reference_dir = os.path.abspath(
            self.reference_dir
        )

        self.words = [
            "HELLO",
            "THANKYOU",
            "SORRY",
            "YES",
            "NO"
        ]

        self.references = {}

        self.load_references()

        print("========================================")
        print("Reference matcher loaded successfully.")
        print("========================================")


    # =========================================================
    # LOAD REFERENCES
    # =========================================================

    def load_references(self):

        total = 0

        for word in self.words:

            word_dir = os.path.join(
                self.reference_dir,
                word
            )

            files = sorted(
                glob.glob(
                    os.path.join(
                        word_dir,
                        "*.npy"
                    )
                )
            )

            self.references[word] = []

            for file in files:

                try:

                    sequence = np.load(
                        file
                    ).astype(
                        np.float32
                    )

                    if sequence.shape != (
                        30,
                        63
                    ):

                        print(
                            f"Skipping invalid: "
                            f"{file}"
                        )

                        continue


                    sequence = self.normalize_sequence(
                        sequence
                    )

                    self.references[word].append(
                        sequence
                    )

                    total += 1

                except Exception as e:

                    print(
                        f"Failed loading "
                        f"{file}: {e}"
                    )


            print(
                f"{word}: "
                f"{len(self.references[word])} "
                f"references"
            )


        print(
            f"Total references: {total}"
        )


    # =========================================================
    # NORMALIZE ONE FRAME
    # =========================================================

    def normalize_frame(
        self,
        frame
    ):

        frame = np.asarray(
            frame,
            dtype=np.float32
        ).reshape(
            21,
            3
        )


        # -----------------------------------------------------
        # Wrist = landmark 0
        # -----------------------------------------------------

        wrist = frame[0].copy()


        # Move wrist to origin

        frame = frame - wrist


        # -----------------------------------------------------
        # Scale normalization
        # -----------------------------------------------------

        distances = np.linalg.norm(
            frame,
            axis=1
        )

        scale = np.max(
            distances
        )


        if scale > 1e-6:

            frame = frame / scale


        return frame.flatten()


    # =========================================================
    # NORMALIZE SEQUENCE
    # =========================================================

    def normalize_sequence(
        self,
        sequence
    ):

        normalized = []

        for frame in sequence:

            normalized.append(
                self.normalize_frame(
                    frame
                )
            )

        return np.asarray(
            normalized,
            dtype=np.float32
        )


    # =========================================================
    # FRAME DISTANCE
    # =========================================================

    def frame_distance(
        self,
        frame1,
        frame2
    ):

        a = frame1.reshape(
            21,
            3
        )

        b = frame2.reshape(
            21,
            3
        )


        # -----------------------------------------------------
        # Landmark position difference
        # -----------------------------------------------------

        position_distance = np.mean(
            np.linalg.norm(
                a - b,
                axis=1
            )
        )


        # -----------------------------------------------------
        # Finger-shape difference
        # -----------------------------------------------------

        shape_distance = np.mean(
            np.abs(
                a - b
            )
        )


        # Combine

        distance = (
            0.7 * position_distance
            +
            0.3 * shape_distance
        )


        return float(
            distance
        )


    # =========================================================
    # SEQUENCE DISTANCE
    # =========================================================

    def sequence_distance(
        self,
        sequence1,
        sequence2
    ):

        n = len(
            sequence1
        )

        m = len(
            sequence2
        )


        # -----------------------------------------------------
        # DTW matrix
        # -----------------------------------------------------

        dtw = np.full(
            (n + 1, m + 1),
            np.inf,
            dtype=np.float32
        )

        dtw[0, 0] = 0.0


        # -----------------------------------------------------
        # DTW
        # -----------------------------------------------------

        for i in range(
            1,
            n + 1
        ):

            for j in range(
                1,
                m + 1
            ):

                cost = self.frame_distance(
                    sequence1[i - 1],
                    sequence2[j - 1]
                )


                previous = min(
                    dtw[i - 1, j],
                    dtw[i, j - 1],
                    dtw[i - 1, j - 1]
                )


                dtw[i, j] = (
                    cost + previous
                )


        # -----------------------------------------------------
        # Normalize by path length
        # -----------------------------------------------------

        distance = (
            dtw[n, m]
            /
            (n + m)
        )


        return float(
            distance
        )


    # =========================================================
    # MATCH
    # =========================================================

    def match(
        self,
        sequence
    ):

        sequence = np.asarray(
            sequence,
            dtype=np.float32
        )


        if sequence.shape != (
            30,
            63
        ):

            raise ValueError(
                f"Expected (30,63), "
                f"got {sequence.shape}"
            )


        # -----------------------------------------------------
        # Normalize webcam sequence
        # -----------------------------------------------------

        sequence = self.normalize_sequence(
            sequence
        )


        results = []


        # =====================================================
        # Compare against every reference
        # =====================================================

        for word in self.words:

            word_distances = []


            for reference in self.references[word]:

                distance = (
                    self.sequence_distance(
                        sequence,
                        reference
                    )
                )


                word_distances.append(
                    distance
                )


            if not word_distances:

                continue


            # -------------------------------------------------
            # Sort distances
            # -------------------------------------------------

            word_distances.sort()


            # -------------------------------------------------
            # Use best 3 references
            # -------------------------------------------------

            top_k = word_distances[
                :min(
                    3,
                    len(word_distances)
                )
            ]


            # Average best matches

            score = float(
                np.mean(
                    top_k
                )
            )


            results.append(
                (
                    word,
                    score
                )
            )


        # =====================================================
        # SORT
        # =====================================================

        results.sort(
            key=lambda x: x[1]
        )


        # =====================================================
        # PRINT RANKING
        # =====================================================

        print()
        print(
            "Dynamic ranking:"
        )

        for word, distance in results:

            print(
                f"  {word:<10} "
                f"{distance:.4f}"
            )


        # =====================================================
        # BEST RESULT
        # =====================================================

        if not results:

            return {
                "word": "UNKNOWN",
                "confidence": 0.0,
                "distance": 999.0
            }


        best_word = results[0][0]
        best_distance = results[0][1]


        # =====================================================
        # SECOND BEST
        # =====================================================

        if len(results) > 1:

            second_distance = (
                results[1][1]
            )

        else:

            second_distance = (
                best_distance + 1.0
            )


        # =====================================================
        # CONFIDENCE
        # =====================================================

        confidence = (
            1.0
            /
            (1.0 + best_distance)
        )


        confidence *= 100.0


        # -----------------------------------------------------
        # Separation bonus
        # -----------------------------------------------------

        if second_distance > 0:

            separation = (
                second_distance
                -
                best_distance
            )

            confidence += (
                separation * 25.0
            )


        confidence = max(
            0.0,
            min(
                99.0,
                confidence
            )
        )


        return {
            "word": best_word,
            "confidence": float(
                confidence
            ),
            "distance": float(
                best_distance
            )
        }