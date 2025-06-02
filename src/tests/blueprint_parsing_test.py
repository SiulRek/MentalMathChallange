import json
import unittest

from core.parse_blueprint_from_text import (
    parse_blueprint_from_text,
    UserConfigError,
)
from core.parse_blueprint_from_text import parse_blueprint_from_text
from core.unparse_blueprint_to_text import unparse_blueprint_to_text
from tests.utils.base_test_case import BaseTestCase


class TestParseBlueprintFromText(BaseTestCase):

    # ---------- Test Cases for Valid Math Blocks ----------
    def test_blueprint_single_operator(self):
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

    def test_with_alternating_elements(self):
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

    def test_float_start_and_end(self):
        blueprint = """math: 1
  float 1.1 2.2
  op *
  float 3.3 4.4
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(len(result[0][0]["elements"]), 3)

    def test_numeric_end(self):
        blueprint = """math: 1
    int 0
    op +
    float 0.0
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(result[0][0]["elements"][0]["type"], "int")
        self.assertEqual(result[0][0]["elements"][1]["value"], "+")
        self.assertEqual(result[0][0]["elements"][-1]["type"], "float")

    def test_float_precision(self):
        blueprint = """math: 1
  float.2 1.1 2.2
  op /
  float.3 3.3 4.4
"""
        result = parse_blueprint_from_text(blueprint)
        elements = result[0][0]["elements"]
        self.assertEqual(elements[0]["type"], "float.2")
        self.assertEqual(elements[0]["start"], 1.1)
        self.assertEqual(elements[0]["end"], 2.2)
        self.assertEqual(elements[-1]["type"], "float.3")
        self.assertEqual(elements[-1]["start"], 3.3)
        self.assertEqual(elements[-1]["end"], 4.4)

    def test_multiple_operators(self):
        blueprint = """math: 1
    int 1 5
    op + - /
    float 2.0 4.0
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(len(result[0][0]["elements"]), 3)
        self.assertEqual(result[0][0]["elements"][1]["value"], ["+", "-", "/"])

    def test_all_supported_operators(self):
        supported = ["+", "-", "*", "/", "//", "%", "**"]
        blueprint_ref = """math: 1
    int 1 5
    op OPERATOR
    float 2.0 4.0
"""
        for operator in supported:
            with self.subTest(operator=operator):
                blueprint = blueprint_ref.replace("OPERATOR", operator)
                result = parse_blueprint_from_text(blueprint)
                elements = result[0][0]["elements"]
                self.assertEqual(len(elements), 3)
                self.assertEqual(elements[1]["type"], "operator")
                self.assertEqual(elements[1]["value"], operator)

    def test_math_expression_with_brackets(self):
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

    def test_math_expression_with_function(self):
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
        self.assertEqual(elements[0]["value"], "sin")

    def _load_supported_functions(self):
        supported = [
            "abs",
            "ceil",
            "floor",
            "round",
            "exp",
            "log",
            "log10",
            "sqrt",
            "sin",
            "cos",
            "tan",
        ]
        return supported

    def test_math_expression_with_all_supported_functions(self):
        blueprint_ref = """math: 1
        func FUNCTION
        (
        int 1 5
        )
        """
        for function in self._load_supported_functions():
            with self.subTest(function=function):
                blueprint = blueprint_ref.replace("FUNCTION", function)
                result = parse_blueprint_from_text(blueprint)
                elements = result[0][0]["elements"]
                self.assertEqual(len(elements), 4)
                self.assertEqual(elements[0]["type"], "function")
                self.assertEqual(elements[0]["value"], function)

    def _load_supported_constants(self):
        supported = [
            "c",
            "h",
            "hbar",
            "G",
            "e",
            "k",
            "N_A",
            "R",
            "alpha",
            "mu_0",
            "epsilon_0",
            "sigma",
            "zero_Celsius",
            "pi",
            "Avogadro",
            "Boltzmann",
            "Planck",
            "speed_of_light",
            "elementary_charge",
            "gravitational_constant",
        ]
        return supported

    def test_math_expressions_with_constants(self):
        blueprint = """math: 1
    const pi
    op +
    const mu_0
    """
        result = parse_blueprint_from_text(blueprint)
        elements = result[0][0]["elements"]
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0]["type"], "constant")
        self.assertEqual(elements[0]["value"], "pi")
        self.assertEqual(elements[2]["type"], "constant")
        self.assertEqual(elements[2]["value"], "mu_0")

    def test_math_expressions_with_all_supported_constants(self):
        blueprint_ref = """math: 1
        const CONSTANT
        """
        for constant in self._load_supported_constants():
            with self.subTest(constant=constant):
                blueprint = blueprint_ref.replace("CONSTANT", constant)
                result = parse_blueprint_from_text(blueprint)
                elements = result[0][0]["elements"]
                self.assertEqual(len(elements), 1)
                self.assertEqual(elements[0]["type"], "constant")
                self.assertEqual(elements[0]["value"], constant)

    # ---------- Test Cases for Valid Date Blocks ----------
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

    def test_validate_date_without_any_year(self):
        blueprint = "date: 1\n"
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(result[0][0]["category"], "date")

    # ---------- Test Cases for Mixed Blueprints ----------
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

    def test_inconsistent_spacing(self):
        blueprint = """math:  1
  int  1 5
 op +
    float  2.0   4.0

date: 2
 start   2000
    end    2010
"""
        result = parse_blueprint_from_text(blueprint)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0]["category"], "math")
        self.assertEqual(result[1][0]["category"], "date")

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

    # ---------- Test Cases for Invalid Blueprints ----------
    def test_invalid_missing_indentation(self):
        blueprint = """math: 1
int 1 5
    op +
    float 2.0 4.0
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_unexpected_indentation(self):
        blueprint = """  math: 1
    int 1 5
    op +
    float 2.0 4.0
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_math_block_missing_elements(self):
        blueprint = "math: 1\n"
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_math_invalid_arguments_for_int(self):
        blueprint = """math: 1
    int 1 INVALID
    """
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_math_invalid_arguments_for_float(self):
        blueprint = """math: 1
    float 1.0 INVALID
    """
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_math_invalid_arguments_for_float_precision(self):
        blueprint = """math: 1
    float.2 1.0 INVALID
    """
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

        blueprint = """math: 1
        float.INVALID 1.0 2.0
        """
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_block_header_missing_colon(self):
        blueprint = """math 3
    int 1 10
    op +
    float 2.0 4.0
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_unknown_block_type(self):
        blueprint = """unknown: 1
    int 1 10
    op +
    float 2.0 4.0
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_unknown_expression_type(self):
        blueprint = """int: 1
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

    def test_invalid_function(self):
        blueprint = """math: 1
    func invalid_function
    (
    int 1 5
    )
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_invalid_constant(self):
        blueprint = """math: 1
    const invalid_constant
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

    def test_invalid_token_count_for_func(self):
        blueprint = """math: 1
    func
    int 1 5
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_token_in_block_header(self):
        blueprint = """math: 1 extra
    int 1 5
    op +
    float 2.0 4.0
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_token_in_int(self):
        blueprint = """math: 1
    int 1 5 extra
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_token_in_float(self):
        blueprint = """math: 1
    float 2.0 3.0 extra
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_token_in_const(self):
        blueprint = """math: 1
    const pi extra
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_token_in_func(self):
        blueprint = """math: 1
    func sin extra
    (
    int 1 5
    )
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_token_in_opening_bracket(self):
        blueprint = """math: 1
    ( extra
    int 1 5
    )
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_token_in_closing_bracket(self):
        blueprint = """math: 1
    (
    int 1 5
    ) extra
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_missing_elements_in_math_block(self):
        blueprint = """math: 1
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_date_with_non_numeric_start(self):
        blueprint = """date: 1
    start year2000
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_tokens_in_start(self):
        blueprint = """date: 1
    start 2000 extra
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_extra_tokens_in_end(self):
        blueprint = """date: 1
    end 2020 extra
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_one_line_math_block(self):
        blueprint = "Invalid: 1"
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    def test_only_function_in_math_block(self):
        blueprint = """math: 1
    func sin
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint)

    # ---------- Test Cases for Invalid Math Expressions ----------
    def test_two_consecutive_numeric_elements(self):
        blueprint = """math: 1
    int 1 5
    float 2.0 3.0
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "two consecutive numeric types",
            str(exc.exception),
        )

    def test_two_consecutive_operators(self):
        blueprint = """math: 1
    int 1 5
    op + -
    op *
    int 2 5
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "two consecutive operators",
            str(exc.exception),
        )

    def test_function_not_followed_by_bracket(self):
        blueprint = """math: 1
    func sin
    int 1 5
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "function not followed by an opening bracket",
            str(exc.exception),
        )

    def test_bracket_never_closed_or_not_opened(self):
        blueprint = """math: 1
    (
    int 1 5
    op +
    float 2.0 4.0
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "unmatched brackets",
            str(exc.exception),
        )

    def test_operator_at_the_beginning(self):
        blueprint = """math: 1
    op *
    int 1 5
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "expression starts with an operator",
            str(exc.exception),
        )

    def test_plus_or_minus_allowed_at_the_beginning(self):
        blueprint_ref = """math: 1
    op OPERATOR
    function sin
    (
    )
"""
        for operator in ["+", "-"]:
            with self.subTest(operator=operator):
                blueprint = blueprint_ref.replace("OPERATOR", operator)
                with self.assertRaises(UserConfigError) as exc:
                    parse_blueprint_from_text(blueprint)
                self.assertNotIn(
                    "expression starts with an operator",
                    str(exc.exception),
                )

    def test_operator_at_the_end(self):
        blueprint = """math: 1
    int 1 5
    op +
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "expression ends with an operator",
            str(exc.exception),
        )

    def test_function_at_the_end(self):
        blueprint = """math: 1
    int 1 5
    func sin
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "expression ends with a function",
            str(exc.exception),
        )

    def test_function_preceded_by_numeric(self):
        blueprint = """math: 1
    int 1 5
    func sin
    (
    int 2 5
    )
"""
        with self.assertRaises(UserConfigError) as exc:
            parse_blueprint_from_text(blueprint)
        self.assertIn(
            "function preceded by a numeric type",
            str(exc.exception),
        )


class TestUnparseBlueprintToText(unittest.TestCase):
    def test_round_trip_basic(self):
        blueprint = """math: 1
  int 1 10
  op +
  float 3.0 7.5
"""
        parsed = parse_blueprint_from_text(blueprint)
        reconstructed = unparse_blueprint_to_text(parsed)
        reparsed = parse_blueprint_from_text(reconstructed)
        self.assertEqual(reparsed, parsed)

    def test_round_trip_with_brackets_and_func(self):
        blueprint = """math: 1
  func sin
  (
  int 1 10
  )
  op -
  float.2 1.5 4.5
"""
        parsed = parse_blueprint_from_text(blueprint)
        reconstructed = unparse_blueprint_to_text(parsed)
        reparsed = parse_blueprint_from_text(reconstructed)
        self.assertEqual(reparsed, parsed)

    def test_round_trip_with_constants_and_date(self):
        blueprint = """math: 2
  const pi
  op *
  const mu_0

date: 1
  start 1990
  end 2020
"""
        parsed = parse_blueprint_from_text(blueprint)
        reconstructed = unparse_blueprint_to_text(parsed)
        reparsed = parse_blueprint_from_text(reconstructed)
        self.assertEqual(reparsed, parsed)

    def test_round_trip_with_blueprint_data_as_string(self):
        blueprint = """math: 1
  int 1 5
  op +
  float 2.0 4.0
date: 1
    start 2000
    end 2010
    """
        parsed = parse_blueprint_from_text(blueprint)
        parsed_string = json.dumps(parsed)
        reconstructed = unparse_blueprint_to_text(parsed)
        reparsed = parse_blueprint_from_text(reconstructed)
        self.assertEqual(reparsed, parsed)


if __name__ == "__main__":
    unittest.main()
