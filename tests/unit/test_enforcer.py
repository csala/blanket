from unittest.mock import Mock, patch

from blanket.enforcer import Blanket, get_indentation, is_blank_or_comment


def _configure_path_mock(path_class_mock, source):
    path_object_mock = Mock()
    path_object_mock.read_text.return_value = source
    path_class_mock.return_value = path_object_mock
    return path_object_mock


def test_get_indentation_counts_leading_spaces():
    """Test get_indentation returns the number of leading spaces.

    Input:
        - a line with leading spaces
    Expected Output:
        - integer count of spaces before the first non-space character
    """
    # Setup
    line = "    value = 1\n"

    # Run
    indent = get_indentation(line)

    # Assert
    assert indent == 4


def test_is_blank_or_comment_recognizes_blanks_and_comments():
    """Test is_blank_or_comment classifies blank and comment lines.

    Input:
        - blank line and comment line samples
    Expected Output:
        - True for blank or comment lines, False for code
    """
    # Setup
    blank = "   \n"
    comment = "# comment\n"
    code = "value = 1\n"

    # Run
    blank_result = is_blank_or_comment(blank)
    comment_result = is_blank_or_comment(comment)
    code_result = is_blank_or_comment(code)

    # Assert
    assert blank_result is True
    assert comment_result is True
    assert code_result is False


@patch("blanket.enforcer.Path")
def test_blanket_check_inserts_blank_for_two_level_dedent(path_class_mock):
    """Test Blanket.check inserts a blank line for a two-level dedent.

    Setup:
        - patch blanket.enforcer.Path to return a mock Path with controlled read/write.
    Input:
        - source with a two-level dedent without a blank line
    Expected Output:
        - True is returned for the change
    Expected Side Effects:
        - write_text is called with a blank line inserted
    """
    # Setup
    source = "if True:\n    if True:\n        pass\nprint('hi')\n"
    path_object_mock = _configure_path_mock(path_class_mock, source)

    # Run
    enforcer = Blanket("example.py")
    changed = enforcer.check()

    # Assert
    assert changed is True
    path_object_mock.write_text.assert_called_once()
    written = path_object_mock.write_text.call_args[0][0]
    assert "pass\n\nprint('hi')\n" in written


@patch("blanket.enforcer.Path")
def test_blanket_check_inserts_blank_for_one_level_dedent(path_class_mock):
    """Test Blanket.check inserts a blank line for a one-level dedent.

    Setup:
        - patch blanket.enforcer.Path to return a mock Path with controlled read/write.
    Input:
        - source with a one-level dedent without a blank line
    Expected Output:
        - True is returned for the change
    Expected Side Effects:
        - write_text is called with a blank line inserted
    """
    # Setup
    source = "if True:\n    pass\nprint('hi')\n"
    path_object_mock = _configure_path_mock(path_class_mock, source)

    # Run
    enforcer = Blanket("example.py")
    changed = enforcer.check()

    # Assert
    assert changed is True
    path_object_mock.write_text.assert_called_once()
    written = path_object_mock.write_text.call_args[0][0]
    assert "pass\n\nprint('hi')\n" in written


@patch("blanket.enforcer.Path")
def test_blanket_check_allows_short_continuation_without_blank(path_class_mock):
    """Test Blanket.check allows continuation blocks with three statements or fewer.

    Setup:
        - patch blanket.enforcer.Path to return a mock Path with controlled read/write.
    Input:
        - if/else where the if body has two statements and no blank line before else
    Expected Output:
        - False is returned since no changes are needed
    Expected Side Effects:
        - write_text is not called
    """
    # Setup
    source = "if True:\n    a = 1\n    b = 2\nelse:\n    c = 3\n"
    path_object_mock = _configure_path_mock(path_class_mock, source)

    # Run
    enforcer = Blanket("example.py")
    changed = enforcer.check()

    # Assert
    assert changed is False
    path_object_mock.write_text.assert_not_called()


@patch("blanket.enforcer.Path")
def test_blanket_check_inserts_blank_for_long_continuation(path_class_mock):
    """Test Blanket.check inserts a blank line for long continuation blocks.

    Setup:
        - patch blanket.enforcer.Path to return a mock Path with controlled read/write.
    Input:
        - if/else where the if body has four statements and no blank line before else
    Expected Output:
        - True is returned for the change
    Expected Side Effects:
        - write_text is called with a blank line inserted
    """
    # Setup
    source = (
        "if True:\n"
        "    a = 1\n"
        "    b = 2\n"
        "    c = 3\n"
        "    d = 4\n"
        "else:\n"
        "    e = 5\n"
    )
    path_object_mock = _configure_path_mock(path_class_mock, source)

    # Run
    enforcer = Blanket("example.py")
    changed = enforcer.check()

    # Assert
    assert changed is True
    path_object_mock.write_text.assert_called_once()
    written = path_object_mock.write_text.call_args[0][0]
    assert "d = 4\n\nelse:\n" in written


@patch("blanket.enforcer.Path")
def test_blanket_check_inserts_blank_for_try_except_long_body(path_class_mock):
    """Test Blanket.check inserts a blank line for try/except with a long body.

    Setup:
        - patch blanket.enforcer.Path to return a mock Path with controlled read/write.
    Input:
        - try/except where the try body has four statements and no blank line before except
    Expected Output:
        - True is returned for the change
    Expected Side Effects:
        - write_text is called with a blank line inserted
    """
    # Setup
    source = (
        "try:\n"
        "    a = 1\n"
        "    b = 2\n"
        "    c = 3\n"
        "    d = 4\n"
        "except Exception:\n"
        "    pass\n"
    )
    path_object_mock = _configure_path_mock(path_class_mock, source)

    # Run
    enforcer = Blanket("example.py")
    changed = enforcer.check()

    # Assert
    assert changed is True
    path_object_mock.write_text.assert_called_once()
    written = path_object_mock.write_text.call_args[0][0]
    assert "d = 4\n\nexcept Exception:\n" in written


@patch("blanket.enforcer.Path")
def test_blanket_check_allows_try_finally_short_body(path_class_mock):
    """Test Blanket.check allows try/finally with three statements or fewer.

    Setup:
        - patch blanket.enforcer.Path to return a mock Path with controlled read/write.
    Input:
        - try/finally where the try body has three statements and no blank line before finally
    Expected Output:
        - False is returned since no changes are needed
    Expected Side Effects:
        - write_text is not called
    """
    # Setup
    source = "try:\n" "    a = 1\n" "    b = 2\n" "    c = 3\n" "finally:\n" "    pass\n"
    path_object_mock = _configure_path_mock(path_class_mock, source)

    # Run
    enforcer = Blanket("example.py")
    changed = enforcer.check()

    # Assert
    assert changed is False
    path_object_mock.write_text.assert_not_called()
