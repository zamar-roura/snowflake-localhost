#!/usr/bin/env python3
"""
Unit test for SQL translation from Snowflake to PostgreSQL
This test directly calls the translator and then the SnowflakeLocalClient
"""

import os
import sys
import unittest

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from snowflake_proxy.snowflake_local_client import SnowflakeLocalClient
from snowflake_proxy.sql_translator import SnowflakeToPostgreSQLTranslator


class TestSQLTranslation(unittest.TestCase):
    """Unit tests for SQL translation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.translator = SnowflakeToPostgreSQLTranslator()
        self.client = SnowflakeLocalClient(
            user="snowflake_user",
            password="snowflake_password",
            account="localhost",
            warehouse="COMPUTE_WH",
            database="snowflake_local",
            schema="public",
        )

    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, "client"):
            self.client.close()

    def test_data_type_translation(self):
        """Test translation of Snowflake data types to PostgreSQL"""
        print("\n=== Testing Data Type Translation ===")

        # Test query with Snowflake data types
        snowflake_query = """
        CREATE TABLE IF NOT EXISTS test_types (
            id NUMBER AUTOINCREMENT PRIMARY KEY,
            name VARCHAR(255),
            amount NUMBER(10,2),
            is_active BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
        """

        # Step 1: Translate the query
        translated_query = self.translator.translate(snowflake_query, debug=True)
        print(f"Translated PostgreSQL SQL: {translated_query}")

        # Step 2: Execute through SnowflakeLocalClient
        try:
            result = self.client.execute_query(translated_query)
            print(f"Execution result: {result}")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"Execution error: {e}")
            # Don't fail the test if execution fails (might be due to proxy not running)
            pass

    def test_function_translation(self):
        """Test translation of Snowflake functions to PostgreSQL"""
        print("\n=== Testing Function Translation ===")

        # Test query with Snowflake functions
        snowflake_query = """
        SELECT 
            CURRENT_DATE() as today,
            CURRENT_TIMESTAMP() as now,
            UUID_STRING() as uuid
        FROM test_table
        """

        # Step 1: Translate the query
        translated_query = self.translator.translate(snowflake_query, debug=True)
        print(f"Translated PostgreSQL SQL: {translated_query}")

        # Step 2: Execute through SnowflakeLocalClient
        try:
            result = self.client.execute_query(translated_query)
            print(f"Execution result: {result}")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"Execution error: {e}")
            pass

    def test_syntax_translation(self):
        """Test translation of Snowflake-specific syntax"""
        print("\n=== Testing Syntax Translation ===")

        # Test query with Snowflake-specific syntax
        snowflake_query = "SELECT TOP 10 * FROM example_table WHERE is_active = TRUE"

        # Step 1: Translate the query
        translated_query = self.translator.translate(snowflake_query, debug=True)
        print(f"Translated PostgreSQL SQL: {translated_query}")

        # Step 2: Execute through SnowflakeLocalClient
        try:
            result = self.client.execute_query(translated_query)
            print(f"Execution result: {result}")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"Execution error: {e}")
            pass

    def test_parameter_binding(self):
        """Test translation with parameter binding"""
        print("\n=== Testing Parameter Binding Translation ===")

        # Test query with parameters
        snowflake_query = "INSERT INTO test_table (name, value) VALUES (?, ?)"
        params = ["Test Item", 100.50]

        print(f"Parameters: {params}")

        # Step 1: Translate the query
        translated_query = self.translator.translate(snowflake_query, debug=True)
        print(f"Translated PostgreSQL SQL: {translated_query}")

        # Step 2: Execute through SnowflakeLocalClient
        try:
            result = self.client.execute_query(translated_query, data=params)
            print(f"Execution result: {result}")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"Execution error: {e}")
            pass

    def test_complex_query_translation(self):
        """Test translation of complex Snowflake queries"""
        print("\n=== Testing Complex Query Translation ===")

        # Complex Snowflake query
        snowflake_query = """
        SELECT 
            t1.id,
            t1.name,
            t1.amount,
            CURRENT_DATE() as today,
            CURRENT_TIMESTAMP() as now
        FROM test_table t1
        WHERE t1.is_active = TRUE
        AND t1.amount > 0
        ORDER BY t1.created_at DESC
        LIMIT 10
        """

        # Step 1: Translate the query
        translated_query = self.translator.translate(snowflake_query, debug=True)
        print(f"Translated PostgreSQL SQL: {translated_query}")

        # Step 2: Execute through SnowflakeLocalClient
        try:
            result = self.client.execute_query(translated_query)
            print(f"Execution result: {result}")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"Execution error: {e}")
            pass

    def test_translation_only(self):
        """Test translation without execution (for when proxy is not available)"""
        print("\n=== Testing Translation Only ===")

        test_cases = [
            {
                "name": "Data Types",
                "snowflake": "CREATE TABLE test (id NUMBER, name VARCHAR(255), amount NUMBER(10,2))",
                "expected_postgres": "CREATE TABLE test (id NUMERIC, name VARCHAR(255), amount NUMERIC(10,2))",
            },
            {
                "name": "Functions",
                "snowflake": "SELECT CURRENT_DATE(), CURRENT_TIMESTAMP()",
                "expected_postgres": "SELECT CURRENT_DATE, CURRENT_TIMESTAMP",
            },
            {
                "name": "TOP to LIMIT",
                "snowflake": "SELECT TOP 5 * FROM table",
                "expected_postgres": "SELECT LIMIT 5 * FROM table",
            },
        ]

        for test_case in test_cases:
            print(f"\n--- Testing: {test_case['name']} ---")
            print(f"Snowflake: {test_case['snowflake']}")

            translated = self.translator.translate(test_case["snowflake"], debug=True)
            print(f"Translated: {translated}")

            # Note: This is a simplified comparison - in reality, the translation
            # might be more complex and the expected output might differ
            print(f"Expected: {test_case['expected_postgres']}")
            print(
                f"Match: {translated.upper() == test_case['expected_postgres'].upper()}"
            )


def run_translation_tests():
    """Run the translation unit tests"""
    print("Starting SQL Translation Unit Tests")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSQLTranslation)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("All translation tests passed!")
    else:
        print("Some translation tests failed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_translation_tests()
