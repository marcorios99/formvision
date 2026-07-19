"""Experimental full-field ICR training entrypoint.

This file is intentionally a roadmap stub. The first supported engine uses
foreground segmentation plus MNIST digit classification. A future sequence
model can read the whole student-code ROI end-to-end with CNN + CTC decoding.
"""


def main() -> None:
    print(
        "Sequence ICR training is not implemented yet. "
        "Use training/train_mnist_digit.py for the first supported ICR engine."
    )


if __name__ == "__main__":
    main()
