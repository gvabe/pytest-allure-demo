import os

import allure
import pytest


@allure.feature("Calculator")
@allure.story("Add two numbers")
@pytest.mark.parametrize("left,right,expected", [(2, 3, 5), (-1, 1, 0), (0, 0, 0)])
def test_addition(left, right, expected):
    with allure.step(f"Add {left} and {right}"):
        actual = left + right
    allure.attach(str(actual), name="Actual result", attachment_type=allure.attachment_type.TEXT)
    with allure.step(f"Check the result equals {expected}"):
        assert actual == expected


@allure.feature("Reporting demo")
@allure.title("Optional deliberate failure")
def test_optional_failure():
    """Set DEMO_FAIL=1 to see a failed test in Jenkins and Allure."""
    with allure.step("Check whether the deliberate failure is enabled"):
        assert os.getenv("DEMO_FAIL") != "1", "Intentional demo failure: unset DEMO_FAIL to pass."
