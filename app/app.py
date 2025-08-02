import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from snowflake_proxy.connection_handler import SnowflakeConnectionHandler
from snowflake_proxy.sql_translator import SnowflakeToPostgreSQLTranslator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize components
connection_handler = SnowflakeConnectionHandler()
sql_translator = SnowflakeToPostgreSQLTranslator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "snowflake-localhost-proxy"})

@app.route('/v1/connection', methods=['POST'])
def create_connection():
    """Handle Snowflake connection requests"""
    try:
        data = request.get_json()
        logger.info(f"Received connection request: {data}")
        
        # Extract connection parameters
        connection_params = {
            'user': data.get('user'),
            'password': data.get('password'),
            'account': data.get('account'),
            'warehouse': data.get('warehouse'),
            'database': data.get('database'),
            'schema': data.get('schema'),
            'autocommit': data.get('autocommit', True),
            'session_parameters': data.get('session_parameters')
        }
        
        # Create connection
        connection_id = connection_handler.create_connection(connection_params)
        
        return jsonify({
            "success": True,
            "connection_id": connection_id,
            "message": "Connection created successfully"
        })
    
    except Exception as e:
        logger.error(f"Error creating connection: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/query', methods=['POST'])
def execute_query():
    """Handle Snowflake query execution"""
    try:
        data = request.get_json()
        logger.info(f"Received query request: {data}")
        
        connection_id = data.get('connection_id')
        query = data.get('query')
        params = data.get('params')
        
        if not connection_id or not query:
            return jsonify({
                "success": False,
                "error": "connection_id and query are required"
            }), 400
        
        # Check if debug mode is requested
        debug_mode = data.get('debug', False)
        
        # Translate Snowflake SQL to PostgreSQL
        translated_query = sql_translator.translate(query, debug=debug_mode)
        logger.info(f"Translated query: {translated_query}")
        
        # Execute query
        result = connection_handler.execute_query(connection_id, translated_query, params)
        
        return jsonify({
            "success": True,
            "result": result,
            "original_query": query,
            "translated_query": translated_query
        })
    
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/connection/<connection_id>', methods=['DELETE'])
def close_connection(connection_id):
    """Close a connection"""
    try:
        connection_handler.close_connection(connection_id)
        return jsonify({
            "success": True,
            "message": f"Connection {connection_id} closed successfully"
        })
    
    except Exception as e:
        logger.error(f"Error closing connection: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4566))
    app.run(host='0.0.0.0', port=port, debug=True) 