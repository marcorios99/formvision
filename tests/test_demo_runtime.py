from pathlib import Path

import pytest

from demo.omr_admission import runtime


def _model_path(repo_root: Path) -> Path:
    path = repo_root / "formvision" / "models" / "mnist_digit_prototypes.npz"
    path.parent.mkdir(parents=True)
    path.touch()
    return path


def test_runtime_builds_real_engine_types(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    created = []

    class FakeIcrEngine:
        def __init__(self, model_path) -> None:
            created.append(("icr", model_path))

    class FakeOcrEngine:
        def __init__(self, cache_dir) -> None:
            created.append(("ocr", cache_dir))

    _model_path(tmp_path)
    monkeypatch.setattr(runtime, "MnistDigitIcrEngine", FakeIcrEngine)
    monkeypatch.setattr(runtime, "DoctrOcrEngine", FakeOcrEngine)

    demo_runtime = runtime.build_demo_runtime(tmp_path)

    assert [name for name, _ in created] == ["icr", "ocr"]
    assert demo_runtime.ocr_engine == "doctr"
    assert demo_runtime.icr_engine == "mnist_icr"


def test_runtime_missing_icr_model_is_actionable(tmp_path: Path) -> None:
    with pytest.raises(runtime.DemoEngineError) as error:
        runtime.build_demo_runtime(tmp_path)

    message = str(error.value)
    assert "mnist_digit_prototypes.npz" in message
    assert "python training/train_mnist_digit.py" in message
    assert "data/external/mnist" in message


def test_runtime_missing_doctr_is_actionable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeIcrEngine:
        def __init__(self, model_path) -> None:
            pass

    def missing_doctr(**kwargs):
        raise RuntimeError("docTR is not installed")

    _model_path(tmp_path)
    monkeypatch.setattr(runtime, "MnistDigitIcrEngine", FakeIcrEngine)
    monkeypatch.setattr(runtime, "DoctrOcrEngine", missing_doctr)

    with pytest.raises(runtime.DemoEngineError, match=r'python -m pip install -e "\.\[ocr\]"'):
        runtime.build_demo_runtime(tmp_path)


def test_runtime_reports_doctr_weight_initialization_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeIcrEngine:
        def __init__(self, model_path) -> None:
            pass

    def unavailable_weights(**kwargs):
        raise RuntimeError("connection refused")

    _model_path(tmp_path)
    monkeypatch.setattr(runtime, "MnistDigitIcrEngine", FakeIcrEngine)
    monkeypatch.setattr(runtime, "DoctrOcrEngine", unavailable_weights)

    with pytest.raises(runtime.DemoEngineError) as error:
        runtime.build_demo_runtime(tmp_path)

    message = str(error.value)
    assert "first use may require a network connection" in message
    assert "doctr_cache" in message
    assert "connection refused" in message


def test_runtime_propagates_unexpected_icr_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FailingIcrEngine:
        def __init__(self, model_path) -> None:
            raise RuntimeError("programming failure")

    _model_path(tmp_path)
    monkeypatch.setattr(runtime, "MnistDigitIcrEngine", FailingIcrEngine)
    monkeypatch.setattr(
        runtime,
        "DoctrOcrEngine",
        lambda **kwargs: pytest.fail("docTR must not be constructed after an unexpected ICR error."),
    )

    with pytest.raises(RuntimeError, match="programming failure"):
        runtime.build_demo_runtime(tmp_path)
