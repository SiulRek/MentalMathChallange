import unittest

from src.core.parse_config_from_text import (
    _parse_config_from_text,
    UserConfigError,
)
from src.tests.utils.base_test_case import BaseTestCase


class TestParseConfigFromText(BaseTestCase):

    def test_valid_math_config_single_operator(self):
        config = """math: 2
  int 1 10
  op +
  float 3.0 7.5
"""
        result = _parse_config_from_text(config)
        expected = [
            {
                "category": "math",
                "elements": [
                    {"type": "int", "start": 1, "end": 10},
                    {"type": "operator", "value": "+"},
                    {"type": "float", "start": 3.0, "end": 7.5},
                ],
            },
            2,
        ]
        self.assertEqual(result, [tuple(expected)])

    def test_valid_math_with_alternating_elements(self):
        config = """math: 1
  int 1 5
  op -
  float 2.5 5.5
"""
        result = _parse_config_from_text(config)
        self.assertEqual(result[0][0]["category"], "math")
        self.assertEqual(len(result[0][0]["elements"]), 3)

    def test_valid_math_with_float_start_and_end(self):
        config = """math: 1
  float 1.1 2.2
  op *
  float 3.3 4.4
"""
        result = _parse_config_from_text(config)
        self.assertEqual(result[0][0]["elements"][0]["type"], "float")
        self.assertEqual(result[0][0]["elements"][-1]["type"], "float")

    def test_valid_date_config(self):
        config = """date: 1
  start 1990
  end 2020
"""
        result = _parse_config_from_text(config)
        expected = [
            {
                "category": "date",
                "start_year": 1990,
                "end_year": 2020,
            },
            1,
        ]
        self.assertEqual(result, [tuple(expected)])

    def test_multiple_blocks(self):
        config = """math: 1
  int 1 5
  op *
  float 2.0 4.0

date: 2
  start 2000
  end 2010
"""
        result = _parse_config_from_text(config)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0]["category"], "math")
        self.assertEqual(result[1][0]["category"], "date")

    def test_invalid_block_header_missing_colon(self):
        config = """math 3
  int 1 10
  op +
  float 2.0 4.0
"""
        with self.assertRaises(UserConfigError):
            _parse_config_from_text(config)

    def test_unknown_expression_type(self):
        config = """logic: 1
  gate and
"""
        with self.assertRaises(UserConfigError):
            _parse_config_from_text(config)

    def test_invalid_operator(self):
        config = """math: 1
  int 1 10
  op &
  int 2 5
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config)

    def test_invalid_token_count_for_int(self):
        config = """math: 1
  int
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config)

    def test_invalid_token_count_for_float(self):
        config = """math: 1
  float
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config)

    def test_invalid_token_count_for_op(self):
        config = """math: 1
  int 1 10
  op
  int 2 5
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config)

    def test_missing_elements_in_math_block(self):
        config = """math: 1
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config)

    def test_invalid_math_no_numeric_start(self):
        config = """math: 1
  op +
  int 1 10
"""
        with self.assertRaises(AssertionError) as cm:
            _parse_config_from_text(config)
        self.assertIn(
            "First element must be of type int or float", str(cm.exception)
        )

    def test_invalid_math_no_numeric_end(self):
        config = """math: 1
  float 2.0 3.0
  op -
"""
        with self.assertRaises(AssertionError) as cm:
            _parse_config_from_text(config)
        self.assertIn(
            "Last element must be of type int or float", str(cm.exception)
        )

    def test_invalid_math_two_consecutive_numeric_elements(self):
        config = """math: 1
  int 1 5
  float 2.0 3.0
  int 4 6
"""
        with self.assertRaises(AssertionError) as cm:
            _parse_config_from_text(config)
        self.assertIn("must be of different types", str(cm.exception))

    def test_date_with_non_numeric_start(self):
        config = """date: 1
  start year2000
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config)

    def test_extra_tokens_in_date(self):
        config = """date: 1
  start 2000 extra
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config)

    def test_whitespace_and_empty_lines(self):
        config = """


math: 1

  int 1 5

  op +
  float 2.0 4.0
"""
        result = _parse_config_from_text(config)
        self.assertEqual(result[0][0]["category"], "math")
        self.assertEqual(len(result[0][0]["elements"]), 3)

    def test_operator_multiple_values(self):
        config = """math: 1
  int 1 5
  op + - /
  float 5.0 7.0
"""
        result = _parse_config_from_text(config)
        self.assertEqual(result[0][0]["elements"][1]["value"], ["+", "-", "/"])


if __name__ == "__main__":
    unittest.main()