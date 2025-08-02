import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SnowflakeToPostgreSQLTranslator:
    """Translates Snowflake SQL syntax to PostgreSQL syntax"""

    def __init__(self):
        # Snowflake to PostgreSQL data type mappings
        self.data_type_mappings = {
            "NUMBER": "NUMERIC",
            "DECIMAL": "NUMERIC",
            "INT": "INTEGER",
            "INTEGER": "INTEGER",
            "BIGINT": "BIGINT",
            "SMALLINT": "SMALLINT",
            "FLOAT": "REAL",
            "FLOAT4": "REAL",
            "FLOAT8": "DOUBLE PRECISION",
            "DOUBLE": "DOUBLE PRECISION",
            "REAL": "REAL",
            "VARCHAR": "VARCHAR",
            "STRING": "TEXT",
            "TEXT": "TEXT",
            "CHAR": "CHAR",
            "CHARACTER": "CHAR",
            "BOOLEAN": "BOOLEAN",
            "BOOL": "BOOLEAN",
            "DATE": "DATE",
            "TIME": "TIME",
            "TIMESTAMP": "TIMESTAMP",
            "TIMESTAMP_NTZ": "TIMESTAMP",
            "TIMESTAMP_LTZ": "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP_TZ": "TIMESTAMP WITH TIME ZONE",
            "BINARY": "BYTEA",
            "VARBINARY": "BYTEA",
            "VARIANT": "JSONB",
            "OBJECT": "JSONB",
            "ARRAY": "JSONB",
        }

        # Snowflake-specific functions to PostgreSQL equivalents
        self.function_mappings = {
            "CURRENT_TIMESTAMP()": "CURRENT_TIMESTAMP",
            "CURRENT_DATE()": "CURRENT_DATE",
            "CURRENT_TIME()": "CURRENT_TIME",
            "SYSDATE()": "CURRENT_DATE",
            "SYSTIMESTAMP()": "CURRENT_TIMESTAMP",
            "UUID_STRING()": "gen_random_uuid()",
            "RANDOM()": "random()",
            "SEQUENCE.NEXTVAL": "nextval('sequence_name')",  # Placeholder
            "SEQ.NEXTVAL": "nextval('sequence_name')",  # Placeholder
        }

    def translate(self, query: str, debug: bool = False) -> str:
        """Translate Snowflake SQL to PostgreSQL SQL"""
        logger.info(f"Translating query: {query}")

        # Convert to uppercase for easier pattern matching
        original_query = query
        query = query.upper()

        if debug:
            print(f"\n=== SQL Translation Debug ===")
            print(f"Original Snowflake SQL: {original_query}")

        # Apply transformations
        query = self._translate_data_types(query)
        if debug:
            print(f"After data type translation: {query}")

        query = self._translate_functions(query)
        if debug:
            print(f"After function translation: {query}")

        query = self._translate_snowflake_specific_syntax(query)
        if debug:
            print(f"After syntax translation: {query}")

        query = self._translate_identifiers(query)
        if debug:
            print(f"After identifier translation: {query}")

        # Restore original case for identifiers and strings
        query = self._restore_case(query, original_query)

        if debug:
            print(f"Final PostgreSQL SQL: {query}")
            print(f"=== End Translation ===\n")

        logger.info(f"Translated query: {query}")
        return query

    def _translate_data_types(self, query: str) -> str:
        """Translate Snowflake data types to PostgreSQL"""
        for snowflake_type, pg_type in self.data_type_mappings.items():
            # Match data types in CREATE TABLE, ALTER TABLE, etc.
            pattern = rf"\b{snowflake_type}\b"
            query = re.sub(pattern, pg_type, query, flags=re.IGNORECASE)

        return query

    def _translate_functions(self, query: str) -> str:
        """Translate Snowflake functions to PostgreSQL equivalents"""
        for snowflake_func, pg_func in self.function_mappings.items():
            query = query.replace(snowflake_func, pg_func)

        return query

    def _translate_snowflake_specific_syntax(self, query: str) -> str:
        """Translate Snowflake-specific syntax to PostgreSQL"""

        # Remove Snowflake-specific clauses that don't exist in PostgreSQL
        # WAREHOUSE clause
        query = re.sub(r"\bWAREHOUSE\s+\w+", "", query, flags=re.IGNORECASE)

        # ACCOUNT clause
        query = re.sub(r"\bACCOUNT\s+\w+", "", query, flags=re.IGNORECASE)

        # Replace Snowflake's $1, $2 parameter style with PostgreSQL's $1, $2
        # (They're actually the same, but we ensure consistency)

        # Handle Snowflake's special identifiers (double quotes)
        # PostgreSQL uses double quotes for identifiers too, so this is mostly compatible

        # Replace Snowflake's TOP with LIMIT
        query = re.sub(r"\bTOP\s+(\d+)", r"LIMIT \1", query, flags=re.IGNORECASE)

        # Handle Snowflake's MERGE syntax (convert to INSERT ... ON CONFLICT)
        query = self._translate_merge_syntax(query)

        return query

    def _translate_merge_syntax(self, query: str) -> str:
        """Translate Snowflake MERGE to PostgreSQL INSERT ... ON CONFLICT"""
        # This is a simplified translation - full MERGE translation is complex
        if "MERGE" in query:
            logger.warning("MERGE syntax detected - simplified translation applied")
            # For now, just replace MERGE with INSERT (this is a placeholder)
            query = query.replace("MERGE", "INSERT")

        return query

    def _translate_identifiers(self, query: str) -> str:
        """Handle identifier translations"""
        # Snowflake uses UPPER_CASE by default, PostgreSQL uses lower_case
        # But we'll preserve the original case for now

        # Handle schema.table references
        # Snowflake: DATABASE.SCHEMA.TABLE
        # PostgreSQL: SCHEMA.TABLE (no database prefix)
        query = re.sub(r"(\w+)\.(\w+)\.(\w+)", r"\2.\3", query)

        return query

    def _restore_case(self, translated_query: str, original_query: str) -> str:
        """Restore original case for strings and identifiers"""
        # This is a simplified approach - in a real implementation,
        # you'd need more sophisticated parsing to preserve case correctly

        # For now, we'll just return the translated query as-is
        # A more sophisticated implementation would parse the SQL and
        # preserve case for identifiers and string literals
        return translated_query

    def translate_create_table(self, query: str) -> str:
        """Specialized translation for CREATE TABLE statements"""
        # Remove Snowflake-specific options
        query = re.sub(r"\bCLUSTER\s+BY\s+\([^)]+\)", "", query, flags=re.IGNORECASE)
        query = re.sub(r"\bCOPY\s+GRANTS", "", query, flags=re.IGNORECASE)

        return self.translate(query)

    def translate_create_schema(self, query: str) -> str:
        """Specialized translation for CREATE SCHEMA statements"""
        # Remove Snowflake-specific options
        query = re.sub(r"\bMANAGED\s+ACCESS", "", query, flags=re.IGNORECASE)
        query = re.sub(r"\bWITH\s+TAG\s+\([^)]+\)", "", query, flags=re.IGNORECASE)

        return self.translate(query)
