import os
import shutil
import sys
import unittest

from src.tests.utils.test_result_logger import TestResultLogger

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(FILE_DIR, "..", "..", "..", "..")
DATA_DIR = os.path.join(
    ROOT_DIR, "imlresearch", "src", "testing", "image_data"
)


class BaseTestCase(unittest.TestCase):
    """
    Abstract base class for test cases, providing setup and teardown operations
    common across tests.
    """

    remove_temp_dir = True

    @classmethod
    def _infere_test_file_path(cls):
        """
        Infer the file path of the test file.

        Returns
        -------
        str
            The inferred file path.
        """
        module = cls.__module__
        if module in sys.modules:
            return sys.modules[module].__file__

        if len(sys.argv) > 1:
            return sys.argv[
                1
            ]  


        raise FileNotFoundError(
            "Cannot infer test file path."
        )

    @classmethod
    def _compute_output_dir(cls, parent_folder="tests"):
        """
        Compute the test output directory path.

        This method traverses up the file hierarchy until a directory named
        'tests' is found, then returns the path to the 'outputs' subdirectory.

        Parameters
        ----------
        parent_folder : str, optional
            The parent folder name, by default "tests".

        Returns
        -------
        str
            The output directory path.
        """
        current_dir = os.path.dirname(cls._infere_test_file_path())

        while parent_folder not in os.listdir(current_dir):
            current_dir = os.path.dirname(current_dir)
            if current_dir == os.path.dirname(current_dir):
                raise NotADirectoryError(
                    "Tests directory not found in the path hierarchy."
                )

        return os.path.join(current_dir, parent_folder, "outputs")

    @classmethod
    def _get_test_case_title(cls):
        """
        Generate a formatted test case title for logging.

        Returns
        -------
        str
            The formatted test case title.
        """
        name = cls.__name__.removeprefix("Test")
        name = "".join(
            letter if not letter.isupper() else f" {letter}" for letter in name
        ).strip()
        return name.replace("_", " ").replace("  ", " ") + " Test"

    @classmethod
    def _get_test_case_folder_name(cls):
        """
        Generate a formatted test case folder name.

        Returns
        -------
        str
            The formatted test case name.
        """
        name = cls.__name__.removeprefix("Test")
        name = "".join(
            letter if not letter.isupper() else f"_{letter.lower()}"
            for letter in name
        ).strip()
        return name.replace(" ", "").removeprefix("_") + "_test"

    @classmethod
    def setUpClass(cls):
        """
        Class-level setup: create necessary directories and initialize logging.
        """
        cls.root_dir = os.path.normpath(ROOT_DIR)
        cls.data_dir = DATA_DIR
        cls.output_dir = cls._compute_output_dir()
        cls.results_dir = os.path.join(
            cls.output_dir, cls._get_test_case_folder_name()
        )
        cls.temp_dir = os.path.join(cls.output_dir, "temp")

        os.makedirs(cls.output_dir, exist_ok=True)
        os.makedirs(cls.results_dir, exist_ok=True)

        cls.log_file = os.path.join(cls.output_dir, "test_results.log")
        cls.logger = TestResultLogger(cls.log_file)
        cls.logger.log_title(cls._get_test_case_title())

    @classmethod
    def tearDownClass(cls):
        """
        Class-level teardown: remove empty result directories.
        """
        if os.path.exists(cls.results_dir) and not os.listdir(cls.results_dir):
            shutil.rmtree(cls.results_dir)

    def setUp(self):
        """
        Instance-level setup: create a temporary directory for tests.
        """
        os.makedirs(self.temp_dir, exist_ok=True)

    def run(self, result=None):
        """
        Override the run method to log the test outcome.

        Parameters
        ----------
        result : unittest.TestResult, optional
            The result object that will store test outcomes.
        """
        result = super().run(result)
        self.logger.log_test_outcome(result, self._testMethodName)
        return result

    def tearDown(self):
        """
        Instance-level teardown: log test outcome and remove the temp
        directory.
        """
        if os.path.exists(self.temp_dir) and self.remove_temp_dir:
            shutil.rmtree(self.temp_dir)


if __name__ == "__main__":
    mnist_digits_dataset = BaseTestCase.load_mnist_digits_dataset()
    print(mnist_digits_dataset)