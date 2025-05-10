from abc import ABC, abstractmethod
import importlib
import os
import sys
import unittest
from unittest import defaultTestLoader as Loader

from tests.utils.generate_test_results_message import (
    generate_test_results_message,
)
from tests.utils.test_result_logger import TestResultLogger

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class _TestRunnerBase(ABC):
    """
    Base class for running unit tests.

    This class sets up the environment for test execution, including
    initializing loggers and managing test suites. Subclasses should implement
    the `load_tests` method to specify which tests to run.
    """

    def __init__(self):
        self.test_file = self._infere_test_file_path()
        self.output_dir = self._compute_output_dir()
        os.makedirs(self.output_dir, exist_ok=True)
        self._init_logger()
        self.test_suite = unittest.TestSuite()

    def _init_logger(self):
        self.log_file = os.path.join(self.output_dir, "test_results.log")
        TestResultLogger(self.log_file)

    @classmethod
    def _infere_test_file_path(cls):
        module = cls.__module__
        if module in sys.modules:
            return sys.modules[module].__file__
        raise FileNotFoundError(
            "Cannot infer test file path."
        )

    @classmethod
    def _compute_output_dir(cls, parent_folder="tests"):
        current_dir = os.path.dirname(cls._infere_test_file_path())

        while parent_folder not in os.listdir(current_dir):
            current_dir = os.path.dirname(current_dir)
            if current_dir == os.path.dirname(current_dir):
                raise NotADirectoryError(
                    "Tests directory not found in the path hierarchy."
                )

        return os.path.join(current_dir, parent_folder, "outputs")

    @abstractmethod
    def load_tests(self):
        pass

    def load_test_case(self, test_case):
        self.test_suite.addTest(Loader.loadTestsFromTestCase(test_case))

    def load_test_module(self, test_module):
        self.test_suite.addTests(Loader.loadTestsFromModule(test_module))

    def run_tests(self):
        self.load_tests()
        test_result = unittest.TextTestRunner().run(self.test_suite)

        print("\n" + "*" * 35 + "\n")
        print(generate_test_results_message(test_result))
        print()
        print(f"Test results logged to: {self.log_file}")
        print(
            "Test errors logged to: "
            f"{self.log_file.replace('.log', '_errors.log')}"
        )
        print(
            "Simple test results logged to: "
            f"{self.log_file.replace('.log', '_simple.log')}"
        )

        return test_result


class TestRunner(_TestRunnerBase):
    """
    Concrete implementation of the TestRunnerBase class.

    This class implements the load_tests method to specify which tests to run.
    """

    def load_tests(self):
        test_files = []
        print(os.listdir(TEST_DIR))
        for root, _, files in os.walk(TEST_DIR):
            for file in files:
                if file.endswith("_test.py"):
                    test_files.append(os.path.join(root, file))
        test_import_paths = [
            os.path.splitext(os.path.relpath(file))[0].replace(os.sep, ".")
            for file in test_files
        ]
        test_import_paths = [
            test_import_path.removeprefix("src.")
            for test_import_path in test_import_paths
        ]
        test_modules = [
            importlib.import_module(test_import_path)
            for test_import_path in test_import_paths
        ]
        for test_module in test_modules:
            self.load_test_module(test_module)


if __name__ == "__main__":
    test_runner = TestRunner()
    test_runner.run_tests()
