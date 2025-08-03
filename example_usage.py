#!/usr/bin/env python3
"""
Example showing how to modify your existing SnowflakePython class to use the local proxy
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from snowflake_proxy.snowflake_local_client import SnowflakeLocalClient


# Example of how to modify your existing SnowflakePython class
class SnowflakePythonLocal:
    """
    Modified version of your SnowflakePython class that uses the local proxy
    """

    def __init__(
        self,
        user: str | None = None,
        password: str | None = None,
        private_key_path: str | None = None,
        private_key_password: str | None = None,
        account: str | None = None,
        warehouse: str | None = None,
        database: str | None = None,
        schema: str | None = None,
    ) -> None:
        # Initialize the local client instead of real Snowflake
        self.client = SnowflakeLocalClient(
            user=user,
            password=password,
            private_key_path=private_key_path,
            private_key_password=private_key_password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )

    def execute_query(
        self,
        query: str,
        autocommit: bool = True,
        session_parameters: Any = None,
        return_dict: bool = False,
        data: list[str] | dict[str, Any] | None = None,
        use_colon_binding: bool = False,
        verbose: bool = True,
    ) -> Any:
        """Execute a query using the local proxy"""
        return self.client.execute_query(
            query=query,
            autocommit=autocommit,
            session_parameters=session_parameters,
            return_dict=return_dict,
            data=data,
            use_colon_binding=use_colon_binding,
            verbose=verbose,
        )

    def pandas_execute_query(
        self,
        query: str,
        autocommit: bool = True,
        session_parameters: Any = None,
        data: list[str] | None = None,
    ):
        """Execute a query and return pandas DataFrame"""
        return self.client.pandas_execute_query(
            query=query,
            autocommit=autocommit,
            session_parameters=session_parameters,
            data=data,
        )

    def get_columns_info(self, table: str, exclude_ts_ms_column: bool = False):
        """Get column information for a table"""
        return self.client.get_columns_info(table, exclude_ts_ms_column)

    def get_primary_key(self, table: str):
        """Get primary key columns for a table"""
        return self.client.get_primary_key(table)

    def close(self):
        """Close the connection"""
        self.client.close()


def example_usage():
    """Example of how to use the modified class"""

    print("=== Example: Using Modified SnowflakePython Class ===")

    # Create an instance (same interface as your original class)
    snowflake = SnowflakePythonLocal(
        user="snowflake_user",
        password="snowflake_password",
        account="localhost",
        warehouse="COMPUTE_WH",
        database="snowflake_local",
        schema="public",
    )

    try:
        # Your existing code should work with minimal changes
        print("\n1. Testing basic query execution...")
        result = snowflake.execute_query("SELECT * FROM example_table LIMIT 3")
        print(f"Query result: {result}")

        print("\n2. Testing pandas integration...")
        df = snowflake.pandas_execute_query("SELECT * FROM example_table")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame head:\n{df.head()}")

        print("\n3. Testing column information...")
        columns = snowflake.get_columns_info("example_table")
        print(f"Columns: {columns}")

        print("\n4. Testing primary key...")
        pk_columns = snowflake.get_primary_key("example_table")
        print(f"Primary key columns: {pk_columns}")

        print("\n5. Testing CREATE TABLE...")
        create_sql = """
        CREATE TABLE IF NOT EXISTS test_example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            value NUMERIC(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        result = snowflake.execute_query(create_sql)
        print(f"CREATE TABLE result: {result}")

        print("\n6. Testing INSERT with parameters...")
        insert_sql = "INSERT INTO test_example (name, value) VALUES (%s, %s)"
        result = snowflake.execute_query(insert_sql, ["Example Item", 123.45])
        print(f"INSERT result: {result}")

        print("\n7. Testing SELECT with parameters...")
        select_sql = "SELECT * FROM test_example WHERE name = %s"
        result = snowflake.execute_query(select_sql, ["Example Item"])
        print(f"SELECT result: {result}")

    except Exception as e:
        print(f"Error during example: {str(e)}")
        raise
    finally:
        # Clean up
        snowflake.close()
        print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    # Import Any type for type hints
    from typing import Any

    print("Starting SnowflakePython Local Example")
    print("Make sure the Docker containers are running: make start")
    print("=" * 60)

    try:
        example_usage()
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        sys.exit(1)
