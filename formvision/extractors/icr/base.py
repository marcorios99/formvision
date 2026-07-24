from abc import ABC, abstractmethod

import numpy as np

from formvision.extractors.base import Extraction


class IcrEngine(ABC):
    """Interface for handwritten field recognizers."""

    @abstractmethod
    def extract(self, roi: np.ndarray) -> Extraction:
        raise NotImplementedError
