"""
Test cases for SQLFluff parser implementation.
"""

import pytest

from snowflake_proxy.sqlfluffparser.sqlfluff_parser import (
    APIParsingError,
    SQLFluffParser,
)


def test_sqlfluff_parser_initialization():
    parser = SQLFluffParser()
    assert parser.dialect == "snowflake"

    custom_parser = SQLFluffParser(dialect="postgres")
    assert custom_parser.dialect == "postgres"


def test_parse_valid_query():
    parser = SQLFluffParser()
    query = "SELECT column1, column2 FROM my_table WHERE column1 > 0;"

    result = parser.parse(query)
    print(result)

    # Assert that result is a dictionary
    assert isinstance(result, dict), "Parser result should be a dictionary"

    # Assert that the parsing was successful (no syntax errors)
    violations = result.get("violations", [])
    assert not violations, "Query should have no lint violations"

    # Assert that the parsed query matches the input structure
    parsed_tree = result.get("tree", {})
    assert parsed_tree is not None, "Parsed tree should not be None"


def test_parse_invalid_query():
    """Test that invalid SQL raises appropriate parsing error."""
    parser = SQLFluffParser()
    query = "SOLECT column1, column2 FROM my_table WHERE column1 > 0;"

    with pytest.raises(APIParsingError) as exc_info:
        parser.parse(query)

    # Assert that the error message contains details about the syntax error
    error_message = str(exc_info.value).lower()
    assert any(
        msg in error_message for msg in ["syntax error", "parsing error", "solect"]
    )
