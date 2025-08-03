"""
SQLFluff parser implementation for SQL query validation and parsing.
"""

from typing import Any, Dict

import sqlfluff
from sqlfluff.api.simple import APIParsingError


class SQLParsingError(Exception):
    """Error raised when SQL parsing fails."""

    pass


class SQLFluffParser:
    def __init__(self, dialect: str = "snowflake"):
        """
        Initialize SQLFluff parser with specified dialect.

        Args:
            dialect (str): SQL dialect to use for parsing
                           (default: 'snowflake')
        """
        self.dialect = dialect

    def parse(self, sql_query: str) -> Dict[str, Any]:
        """
        Parse and lint SQL query using SQLFluff.

        Args:
            sql_query (str): SQL query string to parse

        Returns:
            Dict[str, Any]: Dictionary containing parsing results and any
                            lint violations

        Raises:
            SQLParsingError: If the query cannot be parsed or contains errors
        """
        # Parse the SQL query
        parsed = sqlfluff.parse(sql_query, dialect=self.dialect)

        # Check for parsing errors
        if parsed.get("violations", []):
            raise SQLParsingError(f"SQL parsing error: {parsed['violations']}")

        return parsed
