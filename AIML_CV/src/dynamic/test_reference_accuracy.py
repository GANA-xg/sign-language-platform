import os
import glob
import numpy as np

from reference_matcher import ReferenceMatcher


matcher = ReferenceMatcher()


print()
print("========================================")
print("REFERENCE SELF TEST")
print("========================================")


total = 0
correct = 0


for word in matcher.words:

    files = sorted(
        glob.glob(
            os.path.join(
                matcher.reference_dir,
                word,
                "*.npy"
            )
        )
    )


    for file in files:

        sequence = np.load(
            file
        ).astype(
            np.float32
        )


        result = matcher.match(
            sequence
        )


        predicted = result["word"]


        total += 1


        if predicted == word:

            correct += 1

            status = "CORRECT"

        else:

            status = "WRONG"


        print(
            f"{word:<10} -> "
            f"{predicted:<10} "
            f"{status}"
        )


print()
print("========================================")
print("REFERENCE TEST RESULT")
print("========================================")

print(
    f"Correct : {correct}/{total}"
)

print(
    f"Accuracy: "
    f"{(correct / total) * 100:.2f}%"
)

print("========================================")