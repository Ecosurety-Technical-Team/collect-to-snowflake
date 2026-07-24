import pytest

from src import casing


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        # tables
        ("dbo.Collection", "DBO_COLLECTION"),
        ("dbo.Company", "DBO_COMPANY"),
        ("dbo.Component", "DBO_COMPONENT"),
        ("dbo.ComponentVerified", "DBO_COMPONENT_VERIFIED"),
        ("dbo.Product", "DBO_PRODUCT"),
        ("dbo.ProductComponent", "DBO_PRODUCT_COMPONENT"),
        ("dbo.ProductVerified", "DBO_PRODUCT_VERIFIED"),
        ("dbo.Regulation", "DBO_REGULATION"),
        ("dbo.SubmissionPeriod", "DBO_SUBMISSION_PERIOD"),
        ("epr.Country", "EPR_COUNTRY"),
        # columns
        ("ProductID", "PRODUCT_ID"),
        ("SomeOtherColumn", "SOME_OTHER_COLUMN"),
    ),
)
def test_pascal_case_to_upper_case(input: str, expected: str) -> None:
    actual = casing.pascal_case_to_upper_case(s=input)
    assert actual == expected
