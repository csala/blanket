from blanket import enforce


def test_enforce_updates_file_with_missing_blank_line(tmp_path):
    """Test enforce updates a file when a blank line is missing.

    Input:
        - a file with a one-level dedent missing a blank line
    Expected Output:
        - True is returned to indicate changes were made
    Expected Side Effects:
        - the file contents include the inserted blank line
    """
    # Setup
    target = tmp_path / "sample.py"
    target.write_text("if True:\n    pass\nprint('hi')\n", encoding="utf-8")

    # Run
    changed = enforce([str(target)])

    # Assert
    assert changed is True
    updated = target.read_text(encoding="utf-8")
    assert "pass\n\nprint('hi')\n" in updated


def test_enforce_leaves_file_unchanged_when_rules_pass(tmp_path):
    """Test enforce leaves a file unchanged when rules already pass.

    Input:
        - a file with a correct blank line between blocks
    Expected Output:
        - False is returned to indicate no changes were made
    Expected Side Effects:
        - the file contents remain the same
    """
    # Setup
    target = tmp_path / "sample.py"
    original = "if True:\n    pass\n\nprint('hi')\n"
    target.write_text(original, encoding="utf-8")

    # Run
    changed = enforce([str(target)])

    # Assert
    assert changed is False
    updated = target.read_text(encoding="utf-8")
    assert updated == original
