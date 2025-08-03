"""
SQLGlot parser implementation for SQL query validation and parsing.
"""

from typing import Any, Dict

from sqlglot import parse as sqlglot_parse


class SQLGlotParser:
    def __init__(self, dialect: str = "snowflake"):
        """
        Initialize SQLGlot parser with specified dialect.

        Args:
            dialect (str): SQL dialect to use for parsing
                          (default: 'snowflake')
        """
        self.dialect = dialect.lower()
        # Map common dialect names to SQLGlot dialect classes
        self.dialect_map = {
            "snowflake": "snowflake",
            "postgres": "postgres",
        }

    def parse(self, sql_query: str, target_dialect: str = None) -> Dict[str, Any]:
        """
        Parse SQL query using SQLGlot and optionally translate to another dialect.

        Args:
            sql_query (str): SQL query string to parse
            target_dialect (str, optional): Target SQL dialect to translate to.
                                          If None, no translation is performed.

        Returns:
            Dict[str, Any]: Dictionary containing parsing results and translated SQL

        Raises:
            Exception: If the query cannot be parsed or contains errors
        """
        try:
            source_dialect = self.dialect_map.get(self.dialect, "snowflake")
            parsed = sqlglot_parse(sql_query, read=source_dialect)

            # If target dialect is specified, generate SQL in that dialect
            sql_output = None
            if target_dialect:
                target_dialect = self.dialect_map.get(target_dialect, target_dialect)
                sql_output = parsed[0].sql(dialect=target_dialect)
            else:
                sql_output = parsed[0].sql()

            # Convert the parse result to a dictionary format
            result = {
                "tree": sql_output,
                "violations": [],  # SQLGlot doesn't have built-in linting
                "success": True,
                "translated_sql": sql_output if target_dialect else None,
            }
            return result

        except Exception as e:
            raise e
