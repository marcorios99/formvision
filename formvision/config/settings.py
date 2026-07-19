from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineSettings:
    """Runtime paths and thresholds used by the demo pipeline."""

    output_dir: Path = Path("data/outputs")
    omr_mark_threshold: float = 0.22
    omr_min_confidence_gap: float = 0.04
    write_debug_images: bool = False
