from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_and_synthetic_clis_expose_separate_commands() -> None:
    runtime = subprocess.run(
        [sys.executable, "-m", "formvision.cli", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    synthetic = subprocess.run(
        [sys.executable, "scripts/synthetic_cli.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "process" in runtime.stdout
    assert "inspect-layout" in runtime.stdout
    assert "generate-sample" not in runtime.stdout
    for command in (
        "generate-sample",
        "generate-omr-sheet",
        "export-mnist-digits",
        "compose-digit-strip",
        "paste-digit-strip",
    ):
        assert command in synthetic.stdout
