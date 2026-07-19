import argparse
import struct
from pathlib import Path

import cv2
import numpy as np


def load_idx_mnist(root: Path) -> tuple[np.ndarray, np.ndarray]:
    images_path = root / "MNIST" / "raw" / "train-images-idx3-ubyte"
    labels_path = root / "MNIST" / "raw" / "train-labels-idx1-ubyte"
    if not images_path.exists() or not labels_path.exists():
        raise FileNotFoundError(
            f"MNIST raw files were not found under {root}. "
            "Download them with torchvision or place the IDX files there."
        )

    with images_path.open("rb") as images_file:
        magic, count, rows, cols = struct.unpack(">IIII", images_file.read(16))
        if magic != 2051:
            raise ValueError(f"Unexpected MNIST image magic number: {magic}")
        images = np.frombuffer(images_file.read(), dtype=np.uint8).reshape(count, rows, cols)

    with labels_path.open("rb") as labels_file:
        magic, label_count = struct.unpack(">II", labels_file.read(8))
        if magic != 2049:
            raise ValueError(f"Unexpected MNIST label magic number: {magic}")
        labels = np.frombuffer(labels_file.read(), dtype=np.uint8)
        if label_count != count:
            raise ValueError("MNIST images and labels have different counts.")

    return images, labels


def normalize_mnist_digit(image: np.ndarray, output_size: int = 28) -> np.ndarray:
    _, binary = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)
    ys, xs = np.where(binary > 0)
    if len(xs) == 0 or len(ys) == 0:
        return np.zeros((output_size, output_size), dtype=np.uint8)

    cropped = binary[max(0, ys.min() - 1) : ys.max() + 2, max(0, xs.min() - 1) : xs.max() + 2]
    scale = min((output_size - 8) / cropped.shape[1], (output_size - 8) / cropped.shape[0])
    new_width = max(1, int(round(cropped.shape[1] * scale)))
    new_height = max(1, int(round(cropped.shape[0] * scale)))
    resized = cv2.resize(cropped, (new_width, new_height), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((output_size, output_size), dtype=np.uint8)
    x_offset = (output_size - new_width) // 2
    y_offset = (output_size - new_height) // 2
    canvas[y_offset : y_offset + new_height, x_offset : x_offset + new_width] = resized
    return canvas


def train_samples(
    images: np.ndarray,
    labels: np.ndarray,
    samples_per_digit: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    prototypes = []
    prototype_labels = []
    model_samples = []
    model_labels = []
    for digit in range(10):
        digit_images = images[labels == digit]
        normalized = np.stack(
            [normalize_mnist_digit(image) for image in digit_images[:samples_per_digit]]
        )
        prototypes.append(np.mean(normalized, axis=0).astype(np.uint8))
        prototype_labels.append(str(digit))
        model_samples.extend(normalized)
        model_labels.extend([str(digit)] * len(normalized))
    return (
        np.stack(prototypes),
        np.array(prototype_labels),
        np.stack(model_samples).astype(np.uint8),
        np.array(model_labels),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a small MNIST prototype ICR model.")
    parser.add_argument("--mnist-root", default="data/external/mnist")
    parser.add_argument("--output", default="formvision/models/mnist_digit_prototypes.npz")
    parser.add_argument("--samples-per-digit", type=int, default=500)
    args = parser.parse_args()

    images, labels = load_idx_mnist(Path(args.mnist_root))
    prototypes, output_labels, samples, sample_labels = train_samples(
        images,
        labels,
        samples_per_digit=args.samples_per_digit,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        prototypes=prototypes,
        labels=output_labels,
        samples=samples,
        sample_labels=sample_labels,
    )
    print(f"Wrote MNIST digit prototype model: {output}")


if __name__ == "__main__":
    main()
