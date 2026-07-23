"""Runtime configuration for the public OMR admission demo."""

from dataclasses import dataclass
import os
from pathlib import Path

from formvision.extractors.icr import MnistDigitIcrEngine
from formvision.extractors.ocr import DoctrOcrEngine
from formvision.pipeline.processor import FormProcessingPipeline


class DemoEngineError(RuntimeError):
    """Raised when the demo's required real recognition engines cannot start."""


@dataclass(frozen=True)
class DemoRuntime:
    """Real engines and pipeline shared by all forms in one demo batch."""

    pipeline: FormProcessingPipeline
    ocr_engine: str = "doctr"
    icr_engine: str = "mnist_icr"


def build_demo_runtime(repo_root: Path) -> DemoRuntime:
    """Build the real OCR/ICR runtime required by the public demo."""
    model_path = repo_root / "formvision" / "models" / "mnist_digit_prototypes.npz"
    cache_dir = Path(os.environ.get("DOCTR_CACHE_DIR", repo_root / "formvision" / "models" / "doctr_cache"))
    if not model_path.is_file():
        raise DemoEngineError(
            "ICR model is missing at {0}. Run `python training/train_mnist_digit.py`; "
            "MNIST IDX files must be available under data/external/mnist.".format(model_path)
        )

    try:
        icr_extractor = MnistDigitIcrEngine(model_path=model_path)
    except (OSError, ValueError, KeyError) as exc:
        raise DemoEngineError(
            "Could not initialize the ICR model at {0}: {1}".format(model_path, exc)
        ) from exc

    try:
        ocr_extractor = DoctrOcrEngine(cache_dir=cache_dir)
    except RuntimeError as exc:
        message = str(exc)
        if "docTR is not installed" in message:
            raise DemoEngineError(
                'docTR is required for the demo. Install it with: python -m pip install -e ".[ocr]"'
            ) from exc
        raise DemoEngineError(
            "Could not initialize docTR pretrained weights. The first use may require a network "
            "connection; weights are cached under {0}. Original error: {1}".format(cache_dir, message)
        ) from exc
    except Exception as exc:
        raise DemoEngineError(
            "Could not initialize docTR pretrained weights. The first use may require a network "
            "connection; weights are cached under {0}. Original error: {1}".format(cache_dir, exc)
        ) from exc

    return DemoRuntime(
        pipeline=FormProcessingPipeline(
            ocr_extractor=ocr_extractor,
            icr_extractor=icr_extractor,
        )
    )
