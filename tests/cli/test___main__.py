# ruff: noqa: S404, S603

import subprocess
import sys
from pathlib import Path


def _run_blanket_cli(repo_root, args):
    process = subprocess.Popen(
        [sys.executable, "-m", "blanket", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def test_cli_returns_nonzero_when_changes_made(tmp_path):
    """Test CLI exits with 1 when it modifies a file.

    Input:
        - a file that needs a blank line inserted
    Expected Output:
        - exit code is 1 and output notes a fix
    Expected Side Effects:
        - the file contents are updated with a blank line
    """
    # Setup
    repo_root = Path(__file__).resolve().parents[2]
    target = tmp_path / "sample.py"
    target.write_text("if True:\n    pass\nprint('hi')\n", encoding="utf-8")

    # Run
    returncode, stdout, stderr = _run_blanket_cli(repo_root, [str(target)])

    # Assert
    assert returncode == 1
    assert "Fixed blank lines in:" in stdout
    assert stderr == ""
    updated = target.read_text(encoding="utf-8")
    assert "pass\n\nprint('hi')\n" in updated


def test_cli_returns_zero_when_no_changes_needed(tmp_path):
    """Test CLI exits with 0 when no changes are needed.

    Input:
        - a file that already follows blank line rules
    Expected Output:
        - exit code is 0 and output is empty
    Expected Side Effects:
        - the file contents remain unchanged
    """
    # Setup
    repo_root = Path(__file__).resolve().parents[2]
    target = tmp_path / "sample.py"
    original = "if True:\n    pass\n\nprint('hi')\n"
    target.write_text(original, encoding="utf-8")

    # Run
    returncode, stdout, stderr = _run_blanket_cli(repo_root, [str(target)])

    # Assert
    assert returncode == 0
    assert stdout == ""
    assert stderr == ""
    updated = target.read_text(encoding="utf-8")
    assert updated == original
