import unittest

from src.core.parse_blueprint_from_text import (
    parse_blueprint_from_text,
    UserConfigError,
)
from src.tests.utils.base_test_case import BaseTestCase


class TestParseBlueprintFromText(BaseTestCase):

    def test_valid_math_blueprint_single_operator(self):
        blueprint = """math: 2
  int 1 10
  op +
  float 3.0 7.5
"""
        result = parse_blueprint_from_text(blueprint)
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
        blueprint = """math: 1
  int 1 5
  op -
  float 2.5 5.5
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(result[0][0]["category"], "math")
        self.assertEqual(len(result[0][0]["elements"]), 3)
        self.assertEqual(result[0][0]["elements"][0]["type"], "int")
        self.assertEqual(result[0][0]["elements"][1]["value"], "-")
        self.assertEqual(result[0][0]["elements"][-1]["type"], "float")

    def test_valid_math_with_float_start_and_end(self):
        blueprint = """math: 1
  float 1.1 2.2
  op *
  float 3.3 4.4
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(len(result[0][0]["elements"]), 3)

    def test_valid_math_with_numeric_end(self):
        blueprint = """math: 1
    int 0
    op +
    float 0.0
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(result[0][0]["elements"][0]["type"], "int")
        self.assertEqual(result[0][0]["elements"][1]["value"], "+")
        self.assertEqual(result[0][0]["elements"][-1]["type"], "float")

    def test_valid_math_with_float_precision(self):
        blueprint = """math: 1
  float.2 1.1 2.2
  op /
  float.3 3.3 4.4
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(result[0][0]["elements"][0]["type"], "float.2")
        self.assertEqual(result[0][0]["elements"][-1]["type"], "float.3")

    def test_valid_math_with_multiple_operators(self):
        blueprint = """math: 1
    int 1 5
    op + - /
    float 2.0 4.0
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(len(result[0][0]["elements"]), 3)
        self.assertEqual(result[0][0]["elements"][1]["value"], ["+", "-", "/"])

    def test_valid_math_with_brackets(self):
        blueprint = """math: 1
    (
    int 1 5
    op +
    float 2.0 4.0
    )
    op -
    int 3 7
"""
        result = parse_blueprint_from_text(blueprint)
        elements = result[0][0]["elements"]
        self.assertEqual(len(elements), 7)
        self.assertEqual(elements[0]["value"], "(")
        self.assertEqual(elements[4]["value"], ")")
    
    def test_valid_math_with_function(self):
        blueprint = """math: 1
    func sin
    (
    int 1 5
    )
    op +
    float 2.0 4.0
"""
        result = parse_blueprint_from_text(blueprint)
        elements = result[0][0]["elements"]
        self.assertEqual(len(elements), 6)
        self.assertEqual(elements[0]["type"], "function")
        self.assertEqual(elements[0]["value"], "np.sin")

    def test_valid_date_blueprint(self):
        blueprint = """date: 1
  start 1990
  end 2020
"""
        result = parse_blueprint_from_text(blueprint)
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
        blueprint = """math: 1
  int 1 5
  op *
  float 2.0 4.0

date: 2
  start 2000
  end 2010
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0]["category"], "math")
        self.assertEqual(result[1][0]["category"], "date")

    def test_invalid_block_header_missing_colon(self):
        blueprint = """math 3
  int 1 10
  op +
  float 2.0 4.0
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_unknown_expression_type(self):
        blueprint = """logic: 1
  gate and
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_operator(self):
        blueprint = """math: 1
  int 1 10
  op &
  int 2 5
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_token_count_for_int(self):
        blueprint = """math: 1
  int
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_token_count_for_float(self):
        blueprint = """math: 1
  float
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_token_count_for_op(self):
        blueprint = """math: 1
  int 1 10
  op
  int 2 5
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_missing_elements_in_math_block(self):
        blueprint = """math: 1
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_math_no_numeric_start(self):
        blueprint = """math: 1
  op **
  int 1 10
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_math_no_numeric_end(self):
        blueprint = """math: 1
  float 2.0 3.0
  op -
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)
        
    def test_invalid_math_two_consecutive_numeric_elements(self):
        blueprint = """math: 1
  int 1 5
  float 2.0 3.0
  int 4 6
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_date_with_non_numeric_start(self):
        blueprint = """date: 1
  start year2000
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_tokens_in_date(self):
        blueprint = """date: 1
  start 2000 extra
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_whitespace_and_empty_lines(self):
        blueprint = """


math: 1

  int 1 5

  op +
  float 2.0 4.0
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(result[0][0]["category"], "math")
        self.assertEqual(len(result[0][0]["elements"]), 3)

    def test_operator_multiple_values(self):
        blueprint = """math: 1
  int 1 5
  op + - /
  float 5.0 7.0
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(result[0][0]["elements"][1]["value"], ["+", "-", "/"])


if __name__ == "__main__":
    unittest.main()