import demo


def test_demo_main_returns_zero_when_batch_passes(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        demo,
        "run_demo_batch",
        lambda root, report_path: {
            "summary": {
                "forms_processed": 10,
                "forms_total": 10,
                "qr": {"correct": 10, "total": 10, "accuracy": 1.0},
                "omr": {"correct": 80, "total": 80, "accuracy": 1.0},
                "passed": True,
            }
        },
    )

    assert demo.main() == 0
    assert "Status: PASS" in capsys.readouterr().out


def test_demo_main_returns_one_when_batch_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        demo,
        "run_demo_batch",
        lambda root, report_path: {
            "summary": {
                "forms_processed": 9,
                "forms_total": 10,
                "qr": {"correct": 9, "total": 10, "accuracy": 0.9},
                "omr": {"correct": 72, "total": 80, "accuracy": 0.9},
                "passed": False,
            }
        },
    )

    assert demo.main() == 1
    assert "Status: FAIL" in capsys.readouterr().out


def test_demo_main_returns_one_for_invalid_demo_inputs(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        demo,
        "run_demo_batch",
        lambda root, report_path: (_ for _ in ()).throw(demo.DemoInputError("missing layout")),
    )

    assert demo.main() == 1
    assert "FormVision demo input error: missing layout" in capsys.readouterr().out
