import logging
from typing import Any

import requests
from snowflake.connector import ProgrammingError

SnowflakeProgrammingError = ProgrammingError


class SnowflakeLocalClient:
    """Modified Snowflake client that connects to local PostgreSQL proxy"""

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
        proxy_url: str = "http://localhost:4566",
    ) -> None:
        logging.getLogger("snowflake.connector").setLevel(logging.WARNING)
        self.log = logging.getLogger(__name__)
        self.user = user
        self.password = password
        self.account = account
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.proxy_url = proxy_url
        self.connection_id = None
        self.pkb = None

        if private_key_path:
            # For local development, we'll skip private key handling
            # but keep the interface compatible
            self.log.warning("Private key authentication not supported in local mode")

    def _get_connection(
        self, autocommit: bool = True, session_parameters: Any = None
    ) -> "LocalSnowflakeConnection":
        """Create a connection to the local proxy"""
        if not self.connection_id:
            # Create connection through proxy
            connection_params = {
                "user": self.user,
                "password": self.password,
                "account": self.account,
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
                "autocommit": autocommit,
                "session_parameters": session_parameters,
            }

            response = requests.post(
                f"{self.proxy_url}/v1/connection",
                json=connection_params,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                raise Exception(f"Failed to create connection: {response.text}")

            result = response.json()
            self.connection_id = result["connection_id"]
            self.log.info(f"Created local connection: {self.connection_id}")

        return LocalSnowflakeConnection(self.connection_id, self.proxy_url, self.log)

    def execute_query(
        self,
        query: str,
        autocommit: bool = True,
        session_parameters: Any = None,
        return_dict: bool = False,
        data: list[str] | dict[str, Any] | None = None,
        use_colon_binding: bool = False,
        verbose: bool = True,
        debug_translation: bool = False,
    ) -> Any:
        if verbose:
            self.log.info("::group::Local Snowflake query")
            self.log.info(query)
            if data is not None:
                self.log.info(f"Data: {data}")
            self.log.info("::endgroup::")

        with self._get_connection(autocommit, session_parameters) as ctx:
            return ctx.execute_query(query, data, return_dict)

    def get_columns_info(
        self, table: str, exclude_ts_ms_column: bool = False
    ) -> list[dict]:
        """Get column information for a table"""
        describe_query = f"SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = '{table}'"

        with self._get_connection() as ctx:
            result = ctx.execute_query(describe_query)

        columns_info = []
        for row in result:
            column_name = row["column_name"]
            data_type = row["data_type"]
            is_pk = False  # We'd need to check constraints for this
            columns_info.append(
                {"column": column_name, "type": data_type, "is_pk": is_pk}
            )

        if exclude_ts_ms_column:
            columns_info = [
                col_info
                for col_info in columns_info
                if str.upper(col_info["column"]) != "TS_MS"
            ]

        return columns_info

    def get_primary_key(self, table: str) -> list[str]:
        """Get primary key columns for a table"""
        pk_query = f"""
        SELECT column_name 
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = '{table}' 
        AND tc.constraint_type = 'PRIMARY KEY'
        """

        with self._get_connection() as ctx:
            result = ctx.execute_query(pk_query)

        return [row["column_name"] for row in result]

    def close(self):
        """Close the connection"""
        if self.connection_id:
            try:
                requests.delete(f"{self.proxy_url}/v1/connection/{self.connection_id}")
                self.connection_id = None
                self.log.info("Connection closed")
            except Exception as e:
                self.log.error(f"Error closing connection: {str(e)}")


class LocalSnowflakeConnection:
    """Mock Snowflake connection that uses the local proxy"""

    def __init__(self, connection_id: str, proxy_url: str, logger):
        self.connection_id = connection_id
        self.proxy_url = proxy_url
        self.log = logger

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Connection cleanup handled by the client
        pass

    def execute_query(
        self,
        query: str,
        data: Any = None,
        return_dict: bool = False,
        debug_translation: bool = False,
    ) -> Any:
        """Execute a query through the proxy"""
        payload = {
            "connection_id": self.connection_id,
            "query": query,
            "params": data,
            "debug": debug_translation,
        }

        response = requests.post(
            f"{self.proxy_url}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 200:
            raise Exception(f"Query execution failed: {response.text}")

        result = response.json()
        if not result["success"]:
            raise Exception(
                f"Query execution failed: {result.get('error', 'Unknown error')}"
            )

        return result["result"]

    def cursor(self, **kwargs):
        """Return a mock cursor"""
        return LocalSnowflakeCursor(self.connection_id, self.proxy_url, self.log)


class LocalSnowflakeCursor:
    """Mock Snowflake cursor"""

    def __init__(self, connection_id: str, proxy_url: str, logger):
        self.connection_id = connection_id
        self.proxy_url = proxy_url
        self.log = logger
        self._results = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, query: str, params: Any = None):
        """Execute a query"""
        payload = {
            "connection_id": self.connection_id,
            "query": query,
            "params": params,
        }

        response = requests.post(
            f"{self.proxy_url}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 200:
            raise Exception(f"Query execution failed: {response.text}")

        result = response.json()
        if not result["success"]:
            raise Exception(
                f"Query execution failed: {result.get('error', 'Unknown error')}"
            )

        self._results = result["result"]

    def fetchall(self):
        """Fetch all results"""
        return self._results or []
