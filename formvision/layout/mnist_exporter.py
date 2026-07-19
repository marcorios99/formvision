from pathlib import Path

import cv2

from formvision.layout.mnist_digits import MnistDigitRenderer


class MnistDigitExporter:
    """Exports random MNIST digit samples as PNG files."""

    def __init__(self, mnist_root: str | Path = "data/external/mnist") -> None:
        self.renderer = MnistDigitRenderer(mnist_root)

    def export_digits(
        self,
        output_dir: str | Path = "data/digits",
        samples_per_digit: int = 5,
    ) -> list[Path]:
        samples = self.renderer._load_samples()
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        exported: list[Path] = []

        for digit in range(10):
            digit_dir = output / str(digit)
            digit_dir.mkdir(parents=True, exist_ok=True)
            for sample_index in range(samples_per_digit):
                image = self.renderer._prepare_digit(samples[digit], height=48)
                path = digit_dir / f"{digit}_{sample_index + 1:02d}.png"
                cv2.imwrite(str(path), image)
                exported.append(path)
        return exported
