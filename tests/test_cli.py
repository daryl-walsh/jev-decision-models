import json
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.prepare_acceptance import prepare


def test_module_and_installed_console_help():
    for command in (
        [sys.executable, "-m", "micrt_monitor", "--help"],
        [str(Path(sys.executable).parent / "micrt-monitor"), "--help"],
    ):
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
        assert result.returncode == 0
        assert "--update-state" in result.stdout


def test_mise_tune_forwards_paths_from_subdirectory(tmp_path):
    saved = tmp_path / "saved responses"
    shutil.copytree("tests/fixtures/responses", saved)
    state = tmp_path / "state.json"
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            "mise",
            "run",
            "tune",
            "--",
            str(saved),
            "--people",
            str(root / "examples/people.csv"),
            "--state",
            str(state),
            "--update-state",
        ],
        cwd=root / "scripts",
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert len(json.loads(state.read_text())) == 10


def test_prepare_acceptance_preserves_source_and_is_idempotent(tmp_path):
    source = tmp_path / "people.csv"
    shutil.copyfile("examples/people.csv", source)
    before = source.read_bytes()
    output = tmp_path / "acceptance.csv"
    selection = ["C54:Alex:Example"]
    assert prepare(source, output, selection) == 1
    first = output.read_bytes()
    assert prepare(source, output, selection) == 1
    assert output.read_bytes() == first
    assert source.read_bytes() == before
