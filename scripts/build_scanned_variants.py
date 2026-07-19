from pathlib import Path

import cv2

from formvision.image_processing.scan_simulator import ScanSimulationConfig, ScanSimulator


def main() -> None:
    source_dir = Path("demo/omr_admission/images/clean")
    output_dir = Path("demo/omr_admission/images/scanned")
    output_dir.mkdir(parents=True, exist_ok=True)

    simulator = ScanSimulator(
        ScanSimulationConfig(
            max_rotation_degrees=1.5,
            max_shift_pixels=8,
            noise_sigma=3.0,
        )
    )

    source_images = sorted(source_dir.glob("student_*.png"))
    for index, source_path in enumerate(source_images, start=1):
        image = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(source_path)
        simulated = simulator.apply(image, seed=1000 + index)
        output_path = output_dir / source_path.name
        cv2.imwrite(str(output_path), simulated)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
