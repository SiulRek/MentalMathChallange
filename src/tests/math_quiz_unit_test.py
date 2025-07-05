from copy import deepcopy
import unittest
from unittest.mock import patch

from quiz.units.exceptions import UserConfigError, UserResponseError
from quiz.units.math_quiz_unit import (
    MathQuizUnit,
    SUPPORTED_OPERATORS,
    SUPPORTED_FUNCTIONS,
    SUPPORTED_CONSTANTS,
)
from tests.utils.base_test_case import BaseTestCase


class MathQuizTransformOptionsToBlueprintUnitTest(BaseTestCase):

    def setUp(self):
        self.int_option = {"key": "int", "args": ["1", "10"]}
        self.float_option = {"key": "float", "args": ["1.0", "10.0"]}
        self.float2_option = {"key": "float.2", "args": ["1.0", "10.0"]}
        self.op_option = {"key": "op", "args": ["+"]}
        self.ops_option = {"key": "op", "args": ["-", "*", "/"]}
        self.func_option = {"key": "func", "args": ["sqrt"]}
        self.bracket_open_option = {"key": "(", "args": []}
        self.bracket_close_option = {"key": ")", "args": []}
        self.constant_option = {"key": "const", "args": ["pi"]}
        self.constant_int_option = {"key": "const", "args": ["10"]}
        self.constant_float_option = {"key": "const", "args": ["3.14"]}
        return super().setUp()

    def _generate_options(self, option_specifiers):
        options = []
        for specifier in option_specifiers:
            if isinstance(specifier, dict):
                opt = specifier
            elif specifier == "int":
                opt = self.int_option
            elif specifier == "float":
                opt = self.float_option
            elif specifier == "float.2":
                opt = self.float2_option
            elif specifier == "op":
                opt = self.op_option
            elif specifier == "func":
                opt = self.func_option
            elif specifier == "bracket_open":
                opt = self.bracket_open_option
            elif specifier == "bracket_close":
                opt = self.bracket_close_option
            elif specifier == "const":
                opt = self.constant_option
            elif specifier == "const_int":
                opt = self.constant_int_option
            elif specifier == "const_float":
                opt = self.constant_float_option
            else:
                raise ValueError(
                    f"Unknown specifier: {specifier}"
                )
            options.append(deepcopy(opt))
        return options

    def test_numeric_valid_simple(self):
        cases = [
            (self.int_option, {"type": "int", "start": 1, "end": 10}),
            (self.float_option, {"type": "float", "start": 1.0, "end": 10.0}),
            (
                self.float2_option,
                {"type": "float.2", "start": 1.0, "end": 10.0},
            ),
            (self.constant_option, {"type": "constant", "value": "pi"}),
            (
                self.constant_int_option,
                {"type": "int", "start": 10, "end": 10},
            ),
            (
                self.constant_float_option,
                {"type": "float", "start": 3.14, "end": 3.14},
            ),
        ]
        for option, expected in cases:
            with self.subTest(option=option):
                blueprint = MathQuizUnit.transform_options_to_blueprint_unit(
                    [option]
                )
                self.assertEqual(len(blueprint["elements"]), 1)
                elem = blueprint["elements"][0]
                self.assertEqual(elem, expected)

    def test_numeric_valid_single_arg(self):
        cases = [
            (
                {"key": "int", "args": ["5"]},
                {"type": "int", "start": 0, "end": 5},
            ),
            (
                {"key": "float", "args": ["5.0"]},
                {"type": "float", "start": 0, "end": 5.0},
            ),
            (
                {"key": "float.2", "args": ["5.0"]},
                {"type": "float.2", "start": 0, "end": 5.0},
            ),
        ]
        for option, expected in cases:
            with self.subTest(option=option):
                blueprint = MathQuizUnit.transform_options_to_blueprint_unit(
                    [option]
                )
                self.assertEqual(len(blueprint["elements"]), 1)
                elem = blueprint["elements"][0]
                self.assertEqual(elem, expected)

    @patch(
        "quiz.units.math_quiz_unit._assert_math_expression_elements",
        return_value=None,
    )
    def test_non_numeric_valid(self, mock_assert):
        cases = [
            (self.op_option, {"type": "operator", "value": ["+"]}),
            (self.ops_option, {"type": "operator", "value": ["-", "*", "/"]}),
            (self.func_option, {"type": "function", "value": "sqrt"}),
            (self.bracket_open_option, {"type": "bracket", "value": "("}),
            (self.bracket_close_option, {"type": "bracket", "value": ")"}),
        ]
        for option, expected in cases:
            with self.subTest(option=option):
                blueprint = MathQuizUnit.transform_options_to_blueprint_unit(
                    [option]
                )
                self.assertEqual(len(blueprint["elements"]), 1)
                elem = blueprint["elements"][0]
                self.assertEqual(elem, expected)

    def test_supported_operators_valid(self):
        for op in SUPPORTED_OPERATORS:
            with self.subTest(op=op):
                op_dict = {"key": "op", "args": [op]}
                specifiers = ["int", op_dict, "int"]
                options = self._generate_options(specifiers)
                blueprint = MathQuizUnit.transform_options_to_blueprint_unit(
                    options
                )
                elem = blueprint["elements"][1]
                self.assertEqual(elem["type"], "operator")
                self.assertEqual(elem["value"], [op])

    def test_supported_functions_valid(self):
        for func in SUPPORTED_FUNCTIONS:
            with self.subTest(func=func):
                func_dict = {"key": "func", "args": [func]}
                specifiers = [
                    func_dict,
                    "bracket_open",
                    "int",
                    "bracket_close",
                ]
                options = self._generate_options(specifiers)
                blueprint = MathQuizUnit.transform_options_to_blueprint_unit(
                    options
                )
                elem = blueprint["elements"][0]
                self.assertEqual(elem["type"], "function")
                self.assertEqual(elem["value"], func)

    def test_supported_constants_valid(self):
        for const in SUPPORTED_CONSTANTS:
            with self.subTest(const=const):
                options = [{"key": "const", "args": [const]}]
                blueprint = MathQuizUnit.transform_options_to_blueprint_unit(
                    options
                )
                elem = blueprint["elements"][0]
                self.assertEqual(elem["type"], "constant")
                self.assertEqual(elem["value"], const)

    def test_invalid_key(self):
        cases = [
            ({"key": "invalid_key", "args": []}),
            ({"key": "float.2d", "args": []}),
        ]
        for option in cases:
            with self.subTest(option=option):
                with self.assertRaises(UserConfigError):
                    MathQuizUnit.transform_options_to_blueprint_unit([option])

    def test_numeric_too_many_args(self):
        cases = [
            ({"key": "int", "args": ["1", "2", "3"]}),
            ({"key": "float", "args": ["1.0", "2.0", "3.0"]}),
            ({"key": "float.2", "args": ["1.0", "2.0", "3.0"]}),
            ({"key": "const", "args": ["pi", "e"]}),
        ]
        for option in cases:
            with self.subTest(option=option):
                with self.assertRaises(UserConfigError):
                    MathQuizUnit.transform_options_to_blueprint_unit([option])

    def test_non_numeric_too_many_args(self):
        cases = [
            ({"key": "func", "args": ["sqrt", "log"]}),
            ({"key": "(", "args": ["some_arg"]}),
            ({"key": ")", "args": ["some_arg"]}),
        ]
        for option in cases:
            with self.subTest(option=option):
                with self.assertRaises(UserConfigError):
                    MathQuizUnit.transform_options_to_blueprint_unit([option])

    def test_numeric_no_args(self):
        cases = [
            {"key": "int", "args": []},
            {"key": "float", "args": []},
            {"key": "float.2", "args": []},
            {"key": "const", "args": []},
        ]
        for option in cases:
            with self.subTest(option=option):
                with self.assertRaises(UserConfigError):
                    MathQuizUnit.transform_options_to_blueprint_unit([option])

    @patch(
        "quiz.units.math_quiz_unit._assert_math_expression_elements",
        return_value=None,
    )
    def test_non_numeric_no_args(self, mock_assert):
        cases = [
            {"key": "op", "args": []},
            {"key": "func", "args": []},
        ]
        for option in cases:
            with self.subTest(option=option):
                with self.assertRaises(UserConfigError):
                    MathQuizUnit.transform_options_to_blueprint_unit([option])

    def test_numeric_invalid_args(self):
        cases = [
            ({"key": "int", "args": ["a", "b"]}),
            ({"key": "int", "args": ["3.14", "3.71"]}),
            ({"key": "int", "args": ["2", "1"]}),
            ({"key": "float", "args": ["a", "b"]}),
            ({"key": "float", "args": ["2.0", "1.0"]}),
            ({"key": "float.2", "args": ["a", "b"]}),
            ({"key": "float.2", "args": ["2.0", "1.0"]}),
            ({"key": "const", "args": ["invalid_constant"]}),
        ]
        for option in cases:
            with self.subTest(option=option):
                with self.assertRaises(UserConfigError):
                    MathQuizUnit.transform_options_to_blueprint_unit([option])

    def test_operator_invalid_arg(self):
        invalid_op = {"key": "op", "args": ["invalid_operator"]}
        specifiers = ["int", invalid_op, "int"]
        options = self._generate_options(specifiers)
        with self.assertRaises(UserConfigError):
            MathQuizUnit.transform_options_to_blueprint_unit(options)

    def test_function_invalid_arg(self):
        invalid_func = {"key": "func", "args": ["invalid_function"]}
        specifiers = [invalid_func, "bracket_open", "int", "bracket_close"]
        options = self._generate_options(specifiers)
        with self.assertRaises(UserConfigError):
            MathQuizUnit.transform_options_to_blueprint_unit(options)

    def test_valid_sequence_short(self):
        options = [
            {"key": "int", "args": ["1", "10"]},
            {"key": "op", "args": ["+"]},
            {"key": "int", "args": ["1", "10"]},
        ]
        blueprint = MathQuizUnit.transform_options_to_blueprint_unit(options)
        self.assertEqual(len(blueprint["elements"]), 3)
        self.assertEqual(blueprint["elements"][0]["type"], "int")
        self.assertEqual(blueprint["elements"][1]["type"], "operator")
        self.assertEqual(blueprint["elements"][2]["type"], "int")

    def test_valid_sequence_long(self):
        specifiers = [
            "func",
            "bracket_open",
            "int",
            "op",
            "const",
            "bracket_close",
            "op",
            "float",
            "op",
            "float.2",
        ]
        options = self._generate_options(specifiers)
        blueprint = MathQuizUnit.transform_options_to_blueprint_unit(options)
        self.assertEqual(len(blueprint["elements"]), 10)
        expected_types = [
            "function",
            "bracket",
            "int",
            "operator",
            "constant",
            "bracket",
            "operator",
            "float",
            "operator",
            "float.2",
        ]
        for i, elem in enumerate(blueprint["elements"]):
            with self.subTest(i=i):

                self.assertEqual(elem["type"], expected_types[i])

    def test_empty_options(self):
        with self.assertRaises(UserConfigError):
            MathQuizUnit.transform_options_to_blueprint_unit([])

    def test_two_consecutive_numeric_types_problem(self):
        types = ["int", "float", "float.2", "const"]
        for i in range(len(types)):
            for j in range(len(types)):
                specifiers = [types[i], types[j]]
                options = self._generate_options(specifiers)
                with self.subTest(specifiers=specifiers):
                    with self.assertRaises(UserConfigError) as exc:
                        MathQuizUnit.transform_options_to_blueprint_unit(
                            options
                        )
                    self.assertIn(
                        "two consecutive numeric types",
                        str(exc.exception),
                    )

    def test_consecutive_operators_problem(self):
        operators = ["op", "op"]
        for i in range(len(operators)):
            for j in range(len(operators)):
                specifiers = [operators[i], operators[j]]
                options = self._generate_options(specifiers)
                with self.subTest(specifiers=specifiers):
                    with self.assertRaises(UserConfigError) as exc:
                        MathQuizUnit.transform_options_to_blueprint_unit(
                            options
                        )
                    self.assertIn(
                        "two consecutive operators",
                        str(exc.exception),
                    )

    def test_function_not_followed_by_bracket(self):
        cases = [
            ["func", "int"],
            ["func", "op", "int"],
            ["bracket_open", "func", "bracket_close"],
        ]
        for specifiers in cases:
            options = self._generate_options(specifiers)
            with self.subTest(specifiers=specifiers):
                with self.assertRaises(UserConfigError) as exc:
                    MathQuizUnit.transform_options_to_blueprint_unit(options)
                self.assertIn(
                    "function not followed by an opening bracket",
                    str(exc.exception),
                )

    def test_bracket_never_closed_or_opened(self):
        cases = [
            ["bracket_open", "int"],
            ["int", "bracket_close"],
            ["bracket_close", "int", "bracket_open"],
        ]
        for specifiers in cases:
            options = self._generate_options(specifiers)
            with self.subTest(specifiers=specifiers):
                with self.assertRaises(UserConfigError) as exc:
                    MathQuizUnit.transform_options_to_blueprint_unit(options)
                exc_msg = str(exc.exception)
                self.assertTrue(
                    "bracket closed without opening" in exc_msg
                    or "unmatched brackets" in exc_msg
                )

    def test_operator_at_beginning(self):
        allowed_ops = ["+", "-"]
        not_allowed_ops = SUPPORTED_OPERATORS - set(allowed_ops)
        for op in not_allowed_ops:
            with self.subTest(op=op):
                options = [
                    {"key": "op", "args": [op]},
                    {"key": "int", "args": ["1", "10"]},
                ]
                with self.assertRaises(UserConfigError) as exc:
                    MathQuizUnit.transform_options_to_blueprint_unit(options)
                self.assertIn(
                    "expression starts with an operator",
                    str(exc.exception),
                )

    def test_operator_at_end(self):
        op = self._generate_options(["int", "op"])
        with self.assertRaises(UserConfigError) as exc:
            MathQuizUnit.transform_options_to_blueprint_unit(op)
        self.assertIn(
            "expression ends with an operator",
            str(exc.exception),
        )

    def test_function_at_end(self):
        func = self._generate_options(["int", "op", "func"])
        with self.assertRaises(UserConfigError) as exc:
            MathQuizUnit.transform_options_to_blueprint_unit(func)
        self.assertIn(
            "expression ends with a function",
            str(exc.exception),
        )

    def test_function_preceded_by_numeric(self):
        specifiers = ["int", "func", "bracket_open", "int", "bracket_close"]
        options = self._generate_options(specifiers)
        with self.assertRaises(UserConfigError) as exc:
            MathQuizUnit.transform_options_to_blueprint_unit(options)
        self.assertIn(
            "function preceded by numeric",
            str(exc.exception),
        )


class MathQuizUnparseOptionsTest(BaseTestCase):
    def test_unparse_options_round_trip(self):
        options = [
            {"key": "func", "args": ["sqrt"]},
            {"key": "(", "args": []},
            {"key": "int", "args": ["1", "10"]},
            {"key": "op", "args": ["+"]},
            {"key": "float", "args": ["1.0", "10.0"]},
            {"key": "op", "args": ["*", "+", "/"]},
            {"key": "float.2", "args": ["1.0", "10.0"]},
            {"key": "op", "args": ["-"]},
            {"key": "const", "args": ["pi"]},
            {"key": ")", "args": []},
        ]
        blueprint = MathQuizUnit.transform_options_to_blueprint_unit(
            deepcopy(options)
        )
        result = MathQuizUnit.unparse_options(blueprint)
        for original, roundtrip in zip(options, result):
            with self.subTest(original=original, roundtrip=roundtrip):
                self.assertEqual(original["key"], roundtrip["key"])
                self.assertEqual(original["args"], roundtrip["args"])


class MathQuizGenerateQuizTest(BaseTestCase):
    def test_generate_long_quiz_valid(self):
        blueprint = {
            "elements": [
                {"type": "function", "value": "sqrt"},
                {"type": "bracket", "value": "("},
                {"type": "int", "start": 1, "end": 1},
                {"type": "operator", "value": "+"},
                {"type": "float.2", "start": 1.0, "end": 1.0},
                {"type": "operator", "value": "*"},
                {"type": "constant", "value": "pi"},
                {"type": "bracket", "value": ")"},
            ],
            "count": 3,
        }

        quizzes = MathQuizUnit.generate_quiz(blueprint)
        self.assertEqual(len(quizzes), 3)

        for q in quizzes:
            self.assertIn("question", q)
            self.assertIn("answer", q)
            self.assertIn("category", q)
            self.assertEqual(q["category"], "math")

            question = q["question"]
            expected_question = "sqrt(1 + 1.00 * pi)"
            self.assertEqual(question, expected_question)
            answer = float(q["answer"])
            expected_answer = (1 + 1.00 * 3.141592653589793) ** (1 / 2)
            self.assertAlmostEqual(answer, expected_answer, places=6)

    def test_generate_random_numeric_quiz(self):
        elements = [
            {"type": "int", "start": -10, "end": 10},
            {"type": "float", "start": -10.0, "end": 10.0},
            {"type": "float.2", "start": -10.0, "end": 10.0},
        ]
        for elem in elements:
            with self.subTest(elem=elem):
                type_ = elem["type"]
                blueprint = {
                    "elements": [elem],
                    "count": 50,
                }
                quiz = MathQuizUnit.generate_quiz(blueprint)
                self.assertEqual(len(quiz), 50)

                for q in quiz:
                    self.assertIn("question", q)
                    self.assertIn("answer", q)
                    self.assertIn("category", q)
                    self.assertEqual(q["category"], "math")
                    question = float(q["question"])
                    if type_ == "int":
                        question = int(question)
                    else:
                        question = round(question)
                    self.assertIn(question, range(-10, 11))

    def test_random_choice_operators(self):
        operators = list(SUPPORTED_OPERATORS)
        blueprint = {
            "elements": [
                {"type": "int", "start": 1, "end": 10},
                {"type": "operator", "value": operators},
                {"type": "int", "start": 1, "end": 10},
            ],
            "count": 50,
        }
        quiz = MathQuizUnit.generate_quiz(blueprint)
        self.assertEqual(len(quiz), 50)

        for q in quiz:
            self.assertIn("question", q)
            self.assertIn("answer", q)
            self.assertIn("category", q)
            self.assertEqual(q["category"], "math")
            question = q["question"]
            op = question.split(" ")[1]
            self.assertIn(op, operators)

    def test_zero_division(self):
        blueprint = {
            "elements": [
                {"type": "int", "start": 1, "end": 10},
                {"type": "operator", "value": ["/"]},
                {"type": "int", "start": 0, "end": 0},
            ],
            "count": 1,
        }
        quiz = MathQuizUnit.generate_quiz(blueprint)
        self.assertEqual(len(quiz), 1)

        for q in quiz:
            self.assertIn("question", q)
            self.assertIn("answer", q)
            self.assertIn("category", q)
            self.assertEqual(q["category"], "math")
            answer = q["answer"]
            self.assertEqual(answer, "nan")


class MathQuizParseUserAnswerTest(BaseTestCase):
    def test_parse_user_answer_valid(self):
        cases = [
            "1",
            "1.0",
            "3.14",
            "3.001e-3",
            1,
            1.0,
            3.14,
            3.001e-3,
        ]
        for user_answer in cases:
            with self.subTest(user_answer=user_answer):
                parsed = MathQuizUnit.parse_user_answer(user_answer)
                self.assertEqual(parsed, str(user_answer))

    def test_parse_user_answer_invalid(self):
        cases = ["abc", "1,000", "3.14.15", "1/2"]
        for user_answer in cases:
            with self.subTest(user_answer=user_answer):
                with self.assertRaises(UserResponseError):
                    MathQuizUnit.parse_user_answer(user_answer)


if __name__ == "__main__":
    unittest.main()
