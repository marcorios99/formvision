import numpy as np


class PerspectiveCorrector:
    """Placeholder for perspective correction in the public demo.

    The demo keeps generated samples aligned. Real deployments can replace this
    class with marker-based or contour-based correction.
    """

    def correct(self, image: np.ndarray) -> np.ndarray:
        return image
