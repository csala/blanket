# Testing Guide

## Introduction

This document provides a detailed guide on how to write, organize, and run tests in this project.

## Running Tests

### Run All Tests

To run all tests in the project, use:

```bash
pytest
```

### Run Specific Tests

To run tests in a specific file:

```bash
pytest tests/unit/test_some_module.py
```

To run a specific test function:

```bash
pytest tests/unit/test_some_module.py::test_function_name
```

### Run Tests with Coverage

To run tests with a coverage report:

```bash
pytest --cov=blanket
```

To generate an HTML coverage report:

```bash
pytest --cov=blanket --cov-report=html
```

## Creating New Tests

### Test Organization

Tests are organized into a `tests` folder, which contains three subfolders:

- `unit`: Contains unit tests for isolated components.
- `integration`: Contains integration tests for testing interactions between components or with
  external systems.
- `cli`: Contains CLI tests that invoke `python -m blanket` using `subprocess.Popen`.

The folder structure mirrors the structure of the application. Tests for modules under `blanket/`
live directly under the corresponding test type without an extra `blanket/` subfolder. For example,
tests for `blanket/enforcer.py` are located in:

- `tests/unit/test_enforcer.py` for unit tests.
- `tests/integration/test_enforcer.py` for integration tests.

### Naming Conventions

- Test files: `test_<module_name>.py` (e.g., `test_utils.py`, `test___init__.py`). For files with
  dunder names such as `__init__.py`, include exactly three underscore characters in the test
  filename (e.g., `test___init__.py`).
- Test functions: Use descriptive names (e.g., `test_function_does_x_when_condition_y`).

## Examples

Suppose we have a module `my_package/my_module.py` that contains a class `MyClass` with a method
`my_method`. Then, the unit test case for this method will be inside
`tests/unit/my_package/test_my_module.py`, in a class called `TestMyClass`, and be called
`test_my_method()`.

```python
# file my_package/my_module.py
class MyClass:

    def my_method(self, ...):
        # ... method code ...

# file tests/unit/my_package/test_my_module.py
class TestMyClass:

    def test_my_method(self, ...):
        # ... test code ...
```

If we instead have a function `init_function` defined inside `my_package/__init__.py`, and want to
write an integration test case, its code will be inside
`tests/integration/my_package/test___init__.py` (note the three underscores in the test module
name), and the test function will be called `test_init_function()`.

```python
# file my_package/__init__.py
def init_function(...):
    # ... function code ...

# file tests/integration/my_package/test___init__.py
def test_init_function(...):
    # ... test code ...
```

## Writing Tests

### Basic Structure

Every test should follow the "Setup, Run, Assert" (SRA) structure, which is often also called
"Arrange, Act, Assert" (AAA):

```python
# Setup
value = some_function()

# Run
result = another_function(value)

# Assert
assert result == expected_result
```

Use comments to clearly separate the sections. This structure not only enforces clarity but also
helps readers understand exactly what is being tested and how the software under test is being used
during the test. By clearly delineating the preparation, execution, and validation phases, tests
become effective complements to documentation. They provide concrete, executable examples that
demonstrate the expected usage and behavior of the code in various scenarios.

### Coding Conventions

Here are some specific coding conventions that must be used when writing tests:

1. unittest.path is used must be used as a decorator, not a context manager

2. Include a docstring with an explanation of how the test works and what it tests. The docstring
   must include a combination of these sections. All of them can be skipped, but the test must have
   at least one of the Expected sections:

   - Setup: Explain what objects are changes are made in the test context to permit its execution.
     include this section only of there is explicit set up code that performs out of the ordinary
     actions that would not be required for normal usage of the code that is being tested, such as
     creating and configuring mocks.
   - Input: Explain what is passed as input to the tested code, if any. The level of detail should
     be enough to understand what makes this test unique, but it should not go down to code level
     detail, since this is already writting a few lines below.
   - Expected Output: Explain what values or objects the test code is expected to return, if any.
   - Expected Side Effects: Explain what side effects should be observed when the tested code is
     run. These are the changes that cannot be observed in the returned outputs, but which must
     have happened somewhere else and which must be checked.

Here is an example of a test for a function that reads the contents of a file, and which we test
using mocks to avoid reading a real file:

```
@patch("module_name.pathlib.Path")
def test__read_file_contents(path_class_mock):
    """Test _read_file_contents function with a valid file path.

    Setup:
        - patch pathlib.Path to return a Path Mock that returns controlled contents.
    Input:
        - path to an imaginary file
    Expected Output:
        - contents of the file that we mocked
    Expected Side Effect:
        - Path must have been created with the given filename, and read_text must
          have been called
    """
    # setup
    path_object_mock = Mock()
    path_object_mock.read_text.return_value = "file contents"
    path_class_mock.return_value = path_object_mock

    # run
    contents = _read_file_contents("path-to-file")

    # assert
    assert contents == "file contents"
    path_class_mock.assert_called_once_with("path-to-file")
    path_object_mock.read_text.assert_called_once()
```

3. The test case functions for a certain function, or test case class methods for certain method
   form the original class, should be grouped together, in an order that makes sense. And the
   groups that correspond to each function or method in the code that is being tested should be put
   in the same order in which they can be found in the original file.

4. When testing classes and their methods, consider calling the method as a class method passing a
   Mock object as `self` instead of creating an instance of the tested object to call the method as
   an instance method.

   Example:

   ```python
   # We have a class that we want to test with a heavy initialization step
   # or with third party dependencies
   class SomeClass:

        def __init__(self, some, arguments):
            self.arttribute = some_heavy_initialization_process_with_third_party_dependencies()
            ...

        def some_method(self, method, arguments):
            ...

    # We do this in the tests
    class TestSomeClass:

        def test_some_method(self):
            # setup
            mocked_self = Mock()
            mocked_self.attribute = Mock()  # or a specific value

            # run
            output = SomeClass.some_method(mocked_self, method, arguments)

    # We do NOT do this in the tests
    class TestSomeClass:

        def test_some_method(self):
            # run
            some_class_instance = SomeClass(with, arguments)   # This step requires extra setup
            output = some_class_instance.some_method(method, arguments)
   ```

### Unit Tests

Unit tests focus on testing individual functions or classes in isolation to ensure they work as
expected. These tests provide fast feedback and serve as the foundation of a robust testing
strategy.

#### Principles

- **Test in Isolation:** Each unit test should focus exclusively on one function or class, ensuring
  it behaves correctly under all scenarios. This reduces complexity and ensures that failures are
  tied directly to the functionality under test.

- **Mock External Dependencies:** Replace dependencies like databases, file systems, or network
  calls with mocks or stubs to isolate the unit under test. This ensures deterministic behavior and
  faster test execution.

- **Test All Code Paths:** For any function or method with conditional branches (`if/else`,
  `try/except`), write separate test cases for each code path to achieve thorough coverage.

#### Example

Suppose we have a function that fetches user data from an external API and processes it. Here’s the
function:

```python
# file myapp/services/user_service.py
import requests

def fetch_user_data(user_id):
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Failed to fetch user data")

    return response.json()
```

We can write a unit test for this function by mocking the external API call:

```python
# file tests/unit/services/test_user_service.py
from unittest.mock import patch

from myapp.services.user_service import fetch_user_data


@patch("myapp.services.user_service.requests.get")
def test_fetch_user_data_success(mock_get):
    # Setup
    user_id = 123
    mock_response = {"id": 123, "name": "John Doe"}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # Run
    result = fetch_user_data(user_id)

    # Assert
    assert result == mock_response
    mock_get.assert_called_once_with(
      f"https://api.example.com/users/{user_id}"
    )
```

### Integration Tests

Integration tests ensure that multiple components work together as expected. They are broader in
scope and may include interactions with external systems like APIs or databases.

- **Test Interactions Between Components:** Verify that components work together seamlessly,
  including the handling of real data or external dependencies.

Example:

```python
import subprocess

def test_cli_help_shows_usage():
    # Run
    result = subprocess.run(
        ["blanket", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    # Assert
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
```

- **Cleanup and Isolation:** Use setup/teardown mechanisms or fixtures to ensure external systems
  are restored to their original state after the test runs. This prevents side effects between
  tests.

Example:

```python
from pathlib import Path

def test_formatter_creates_expected_output(tmp_path):
    # Setup
    source = "def foo():\n    print('hi')\n"
    target = tmp_path / "sample.py"
    target.write_text(source)

    # Run
    formatted = Path(target).read_text()

    # Assert
    assert "def foo()" in formatted
```

Integration tests are slower than unit tests but essential for verifying that the entire system
behaves as intended under realistic conditions.

### CLI Tests

CLI tests validate the behavior of the command-line interface using `subprocess.Popen` and should
live under `tests/cli`.

## Tools

### pytest

The primary testing framework. See [pytest documentation](https://docs.pytest.org/) for details.

### pytest-mock

Facilitates mocking during tests. Key features include:

- `patch`: Replace objects during tests.
- `autospec`: Ensure mocks match the interface of the original object.
- `spy`: Monitor how functions are called during tests.

Example:

```python
from unittest.mock import patch

def test_some_function(mocker):
    mock = mocker.patch("module.function", return_value="mocked_value")
    result = function_that_uses_module_function()
    assert result == "mocked_value"
    mock.assert_called_once()
```

## Advanced Topics

- **Mocking with Context:** Use `patch` for temporary replacements.
- **Parameterization:** Use `@pytest.mark.parametrize` to test with multiple inputs.

## Testing Guidelines

### Good Practices

1. **Single Responsibility:** Each test should validate only one specific behavior. A
   single-responsibility test ensures that any failures can be immediately traced to the specific
   functionality under test, making debugging simpler and more efficient. For example:

```python
# file tests/unit/utils/test_calculator.py
def test_addition_with_positive_numbers():
    # Setup
    a, b = 3, 5
    calculator = Calculator()

    # Run
    result = calculator.add(a, b)

    # Assert
    assert result == 8
```

2. **Statelessness:** Ensure tests do not leave traces or rely on external states. A test should
   not depend on global variables, pre-existing files, or other side effects. This ensures tests
   are predictable and can run in any order. Example of stateless testing with mocks:

```python
from unittest.mock import MagicMock

# file tests/unit/services/test_file_service.py
def test_save_file_creates_file():
    # Setup
    mock_storage = MagicMock()
    service = FileService(storage=mock_storage)
    file_content = b"sample content"

    # Run
    service.save_file("example.txt", file_content)

    # Assert
    mock_storage.write.assert_called_once_with("example.txt", file_content)
```

3. **Descriptive Names:** Use meaningful names for tests and variables. A well-named test should
   clearly communicate its purpose without requiring additional context. Compare:

   - Poor: `test_function` (vague and unhelpful)
   - Good: `test_user_login_fails_with_invalid_credentials`

4. **Consistency:** Follow the "Setup, Run, Assert" structure and testing conventions across the
   entire codebase. This consistency helps maintainers quickly understand the logic of any given
   test.

### Unit Test Principles

- **Avoid external dependencies:** Unit tests should be isolated from databases, networks, or file
  systems. If the code requires such interactions, use mocks or stubs to simulate them. Example:

```python
from unittest.mock import patch

# file tests/unit/handlers/test_email_handler.py
def test_send_email_success():
    # Setup
    with patch("email_handler.SMTPClient.send") as mock_send:
        mock_send.return_value = True
        email_handler = EmailHandler()

        # Run
        result = email_handler.send_email("to@example.com", "Subject", "Body")

        # Assert
        assert result is True
        mock_send.assert_called_once_with("to@example.com", "Subject", "Body")
```

- **Test one functionality per test case:** Each test should focus on one aspect of a function or
  class. For example, if a function has multiple runtime branches (`if/else`, `try/except`), write
  separate test cases for each branch.

### Integration Test Principles

- **Validate interactions between components:** Ensure that modules work together correctly. This
  often involves verifying interactions with external systems, like APIs or databases.

```python
# file tests/integration/cli/test_help_output.py
import subprocess

def test_cli_help_output():
    # Run
    result = subprocess.run(
        ["blanket", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    # Assert
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
```

- **Use setup/teardown mechanisms to ensure isolation:** For example, use fixtures or context
  managers to prepare and clean up resources like database records or temporary files:

```python
# file tests/integration/utils/test_temp_file.py
def test_temp_file_cleanup(tmp_path):
    # Setup
    target = tmp_path / "sample.py"
    target.write_text("print('hello')\n")

    # Run
    contents = target.read_text()

    # Assert
    assert "hello" in contents
```

## Test-Driven Development (TDD)

TDD involves writing tests before implementing the corresponding functionality. This approach
ensures that:

- Code is testable and meets requirements.
- Regression is minimized.

### Recommended Workflow

1. Write a failing test.
2. Implement the functionality.
3. Run tests and verify the new test passes.
4. Refactor if necessary, ensuring all tests still pass.

Adopting TDD fosters high-quality code and ensures that testing remains a priority throughout
development.
