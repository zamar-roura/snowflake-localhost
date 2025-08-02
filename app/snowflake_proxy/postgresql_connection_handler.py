import os
import uuid
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PostgreSQLConnectionHandler:
    """Handles PostgreSQL connections while mimicking Snowflake connection behavior"""
    
    def __init__(self):
        self.connections: Dict[str, psycopg2.extensions.connection] = {}
        self.connection_params: Dict[str, Dict[str, Any]] = {}
        
        # PostgreSQL connection parameters
        self.pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
        self.pg_port = os.environ.get('POSTGRES_PORT', '5432')
        self.pg_db = os.environ.get('POSTGRES_DB', 'snowflake_local')
        self.pg_user = os.environ.get('POSTGRES_USER', 'snowflake_user')
        self.pg_password = os.environ.get('POSTGRES_PASSWORD', 'snowflake_password')
    
    def create_connection(self, connection_params: Dict[str, Any]) -> str:
        """Create a PostgreSQL connection and return a connection ID"""
        try:
            # Generate unique connection ID
            connection_id = str(uuid.uuid4())
            
            # Store connection parameters
            self.connection_params[connection_id] = connection_params
            
            # Create PostgreSQL connection
            pg_connection = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_password
            )
            
            # Set autocommit if specified
            if connection_params.get('autocommit', True):
                pg_connection.autocommit = True
            
            # Store connection
            self.connections[connection_id] = pg_connection
            
            logger.info(f"Created connection {connection_id}")
            return connection_id
            
        except Exception as e:
            logger.error(f"Error creating connection: {str(e)}")
            raise
    
    def execute_query(self, connection_id: str, query: str, params: Optional[list] = None) -> Any:
        """Execute a query on the specified connection"""
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")
        
        try:
            connection = self.connections[connection_id]
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Try to fetch results (for SELECT queries)
            try:
                results = cursor.fetchall()
                # Convert to list of dicts for JSON serialization
                return [dict(row) for row in results]
            except psycopg2.ProgrammingError:
                # No results to fetch (INSERT, UPDATE, DELETE, etc.)
                return {"affected_rows": cursor.rowcount}
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close_connection(self, connection_id: str) -> None:
        """Close a connection"""
        if connection_id in self.connections:
            try:
                self.connections[connection_id].close()
                del self.connections[connection_id]
                del self.connection_params[connection_id]
                logger.info(f"Closed connection {connection_id}")
            except Exception as e:
                logger.error(f"Error closing connection {connection_id}: {str(e)}")
                raise
        else:
            raise ValueError(f"Connection {connection_id} not found")
    
    def get_connection_info(self, connection_id: str) -> Dict[str, Any]:
        """Get information about a connection"""
        if connection_id not in self.connection_params:
            raise ValueError(f"Connection {connection_id} not found")
        
        return self.connection_params[connection_id]
    
    def list_connections(self) -> list[str]:
        """List all active connection IDs"""
        return list(self.connections.keys()) 