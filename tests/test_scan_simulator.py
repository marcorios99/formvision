import numpy as np

from synthetic.scan_simulator import ScanSimulationConfig, ScanSimulator


def test_scan_simulator_preserves_image_shape():
    image = np.full((120, 80, 3), 255, dtype=np.uint8)

    simulated = ScanSimulator(ScanSimulationConfig()).apply(image, seed=1)

    assert simulated.shape == image.shape
    assert np.array_equal(simulated, ScanSimulator(ScanSimulationConfig()).apply(image, seed=1))
