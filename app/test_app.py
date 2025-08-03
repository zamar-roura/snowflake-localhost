import pytest

from snowflake_local_client import SnowflakeMockClient


def test_snowflake_create_table():
    """Test that a Snowflake CREATE TABLE statement works successfully"""
    # Create a mock client
    client = SnowflakeMockClient(
        user="test_user",
        password="test_pass",
        account="test_account",
        warehouse="test_warehouse",
        database="test_db",
        schema="public",
    )

    try:
        # Test Snowflake CREATE TABLE syntax
        snowflake_query = """
        CREATE TABLE customers (
            customer_id NUMBER PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(255),
            created_at TIMESTAMP_NTZ(9)
        )
        """

        # Execute query - should succeed with Snowflake syntax
        result = client.execute_query(snowflake_query)
        assert result is not None

    finally:
        # Cleanup
        client.close()


def test_postgresql_create_table_fails():
    """Test that a PostgreSQL CREATE TABLE statement fails appropriately"""
    # Create a mock client
    client = SnowflakeMockClient(
        user="test_user",
        password="test_pass",
        account="test_account",
        warehouse="test_warehouse",
        database="test_db",
        schema="public",
    )

    try:
        # Test PostgreSQL CREATE TABLE syntax
        postgresql_query = """
        CREATE TABLE customers (
            customer_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(255),
            created_at TIMESTAMP WITHOUT TIME ZONE
        )
        """

        # Execute query - should fail with PostgreSQL syntax
        with pytest.raises(Exception) as exc_info:
            client.execute_query(postgresql_query)

        # Verify that the error message indicates a failure
        assert "Query execution failed" in str(exc_info.value)

    finally:
        # Cleanup
        client.close()
