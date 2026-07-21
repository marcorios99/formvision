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


def test_runtime_process_requires_real_engines_for_demo_layout() -> None:
    help_result = subprocess.run(
        [sys.executable, "-m", "formvision.cli", "process", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "formvision.cli",
            "process",
            "--image",
            "missing.png",
            "--layout",
            "demo/omr_admission/template/layout.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert "{demo" not in help_result.stdout
    assert "{mnist}" in help_result.stdout
    assert "{doctr}" in help_result.stdout
    assert result.returncode != 0
    assert "ICR fields require --icr-engine mnist." in result.stderr
    assert "Traceback" not in result.stderr
