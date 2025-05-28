import unittest
from unittest.mock import patch, MagicMock

from app.validators import (
    assert_username,
    assert_email,
    assert_password,
    assert_unique_username_and_email,
)
from tests.utils.base_test_case import BaseTestCase


class TestValidators(BaseTestCase):

    # --- assert_username ---

    def test_assert_username_empty(self):
        with self.assertRaisesRegex(
            AssertionError, "Username cannot be empty."
        ):
            assert_username("")

    def test_assert_username_too_short(self):
        with self.assertRaisesRegex(
            AssertionError, "Username must be at least 3 characters long."
        ):
            assert_username("ab")

    def test_assert_username_non_alphanumeric(self):
        with self.assertRaisesRegex(
            AssertionError, "Username must be alphanumeric."
        ):
            assert_username("user@")

    def test_assert_username_too_long(self):
        with self.assertRaisesRegex(
            AssertionError, "Username cannot be longer than 32 characters."
        ):
            assert_username("a" * 33)

    def test_assert_username_valid(self):
        assert_username("ValidUser123")  # Should not raise

    # --- assert_email ---

    def test_assert_email_empty(self):
        with self.assertRaisesRegex(AssertionError, "Email cannot be empty."):
            assert_email("")

    def test_assert_email_missing_at(self):
        with self.assertRaisesRegex(AssertionError, "Invalid email format."):
            assert_email("email.com")

    def test_assert_email_missing_dot(self):
        with self.assertRaisesRegex(AssertionError, "Invalid email format."):
            assert_email("email@domain")

    def test_assert_email_valid(self):
        assert_email("user@example.com")  # Should not raise

    # --- assert_password ---

    def test_assert_password_empty(self):
        with self.assertRaisesRegex(
            AssertionError, "Password cannot be empty."
        ):
            assert_password("")

    def test_assert_password_too_short(self):
        with self.assertRaisesRegex(
            AssertionError, "Password must be at least 6 characters long."
        ):
            assert_password("A2#")

    def test_assert_password_no_digit(self):
        with self.assertRaisesRegex(
            AssertionError, "Password must contain at least one digit."
        ):
            assert_password("Abcdef!")

    def test_assert_password_no_letter(self):
        with self.assertRaisesRegex(
            AssertionError, "Password must contain at least one letter."
        ):
            assert_password("123456!")

    def test_assert_password_no_special_char(self):
        with self.assertRaisesRegex(
            AssertionError,
            "Password must contain at least one special character.",
        ):
            assert_password("Abc123")

    def test_assert_password_too_long(self):
        long_pwd = "a2#" + "x" * 126
        with self.assertRaisesRegex(
            AssertionError, "Password cannot be longer than 128 characters."
        ):
            assert_password(long_pwd)
    
    def test_assert_password_no_uppercase(self):
        with self.assertRaisesRegex(
            AssertionError, "Password must contain at least one uppercase letter."
        ):
            assert_password("abc123!@#")

    def test_assert_password_valid(self):
        assert_password("Abc123!@#")  # Should not raise

    # --- assert_unique_username_and_email ---

    @patch("app.validators.User")
    def test_assert_unique_username_and_email_exists(self, mock_user):
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = True
        mock_user.query = mock_query

        with self.assertRaisesRegex(
            AssertionError, "Username or email already exists in the system."
        ):
            assert_unique_username_and_email(
                "existinguser", "existing@example.com"
            )

    @patch("app.validators.User")
    def test_assert_unique_username_and_email_valid(self, mock_user):
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user.query = mock_query

        assert_unique_username_and_email(
            "newuser", "new@example.com"
        )  # Should not raise


if __name__ == "__main__":
    unittest.main()
