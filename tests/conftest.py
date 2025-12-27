from _pytest.main import ExitCode


def pytest_sessionfinish(session, exitstatus):
    """Suppress exit code 5 when no tests exist yet in the project."""
    if exitstatus == ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = ExitCode.OK


# Add any pytest fixtures here that should be available to all tests
