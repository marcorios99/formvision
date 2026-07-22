import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "formvision"
FORBIDDEN_ROOTS = {"demo", "synthetic", "training", "tools", "scripts"}
RETIRED_CORE_PATHS = (
    "formvision/evaluation",
    "formvision/layout/synthetic_templates.py",
    "formvision/layout/form_overlay.py",
    "formvision/layout/digit_strip.py",
    "formvision/layout/mnist_digits.py",
    "formvision/layout/mnist_exporter.py",
    "formvision/image_processing/scan_simulator.py",
    "formvision/extractors/ocr/demo.py",
    "formvision/extractors/icr_extractor.py",
    "formvision/extractors/ocr_extractor.py",
)


def _forbidden_imports() -> list[str]:
    violations = []
    for path in CORE.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative_path = path.relative_to(ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in FORBIDDEN_ROOTS:
                        violations.append(
                            f"{relative_path}:{node.lineno}: imports forbidden module '{alias.name}'"
                        )
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                root = node.module.split(".", 1)[0]
                if root in FORBIDDEN_ROOTS:
                    violations.append(
                        f"{relative_path}:{node.lineno}: imports forbidden module '{node.module}'"
                    )
    return violations


def test_core_does_not_import_external_project_layers() -> None:
    violations = _forbidden_imports()

    assert not violations, "\n".join(violations)


def test_retired_components_are_absent_from_core() -> None:
    unexpected_paths = [path for path in RETIRED_CORE_PATHS if (ROOT / path).exists()]

    assert not unexpected_paths, "Retired Core components found:\n" + "\n".join(unexpected_paths)


def test_public_package_discovery_is_limited_to_formvision() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'include = ["formvision*"]' in pyproject, (
        "The public distribution must contain only formvision* packages."
    )
