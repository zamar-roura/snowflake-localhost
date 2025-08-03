"""
Test cases for SQLGlot parser implementation.
"""

import pytest
from sqlglot import ParseError

from snowflake_proxy.sqlglotparser.sqlglot_parser import SQLGlotParser


def test_sqlglot_parser_initialization():
    parser = SQLGlotParser()
    assert parser.dialect == "snowflake"

    custom_parser = SQLGlotParser(dialect="postgres")
    assert custom_parser.dialect == "postgres"


def test_parse_valid_query():
    parser = SQLGlotParser()
    query = "SELECT column1, column2 FROM my_table WHERE column1 > 0;"

    result = parser.parse(query)
    print(result)


def test_parse_invalid_query():
    """Test that invalid SQL raises appropriate parsing error."""
    parser = SQLGlotParser()
    query = "SOsLECT column1, column2 FROM my_table WHERE column1 > 0;"

    with pytest.raises(ParseError):
        parser.parse(query)
