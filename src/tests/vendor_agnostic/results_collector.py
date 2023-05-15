import time
import pytest


class ResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        if isinstance(exitstatus, int):
            self.exitcode = exitstatus
        else:
            self.exitcode = exitstatus.value

        self.passed = len(terminalreporter.stats.get("passed", []))
        self.failed = len(terminalreporter.stats.get("failed", []))
        self.xfailed = len(terminalreporter.stats.get("xfailed", []))
        self.skipped = len(terminalreporter.stats.get("skipped", []))

        self.total_duration = time.time() - terminalreporter._sessionstarttime
