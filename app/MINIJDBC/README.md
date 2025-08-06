# MiniJDBC Driver

A minimal JDBC driver implementation that connects to your custom endpoint instead of Snowflake Cloud Service.

## Features

- Basic JDBC driver implementation
- HTTP-based communication with your endpoint
- Support for basic SQL operations (execute, executeQuery, executeUpdate)
- Simple connection management
- JSON-based protocol

## Usage

1. Add the dependency to your project:

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>minijdbc</artifactId>
    <version>1.0-SNAPSHOT</version>
</dependency>
```

2. Use the driver in your code:

```java
// Register the driver (optional as it auto-registers)
Class.forName("com.example.minijdbc.MiniDriver");

// Create a connection
String url = "jdbc:mini://localhost:8080";
Connection conn = DriverManager.getConnection(url);

// Execute a query
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM my_table");

// Process results
while (rs.next()) {
    String value = rs.getString("column_name");
    // Process the value
}
```

## Expected Endpoint API

Your endpoint should implement the following HTTP API:

### Execute SQL Statement
- **URL**: `/execute`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
    "sql": "YOUR SQL STATEMENT"
}
```
- **Response Format for Queries**:
```json
{
    "resultSet": {
        "columns": ["column1", "column2"],
        "rows": [
            {"column1": "value1", "column2": "value2"},
            {"column1": "value3", "column2": "value4"}
        ]
    }
}
```
- **Response Format for Updates**:
```json
{
    "updateCount": 1
}
```
- **Error Response**:
```json
{
    "error": "Error message"
}
```

## Limitations

This is a minimal implementation and has the following limitations:

1. Basic SQL execution only
2. No prepared statements
3. No batch operations
4. Limited data type support
5. No transaction management
6. No metadata support
7. No connection pooling

## Building from Source

```bash
mvn clean install
```

## Testing

To run the tests:

```bash
mvn test
```

## Security Considerations

1. This is a basic implementation and should not be used in production without proper security enhancements
2. Consider adding:
   - SSL/TLS support
   - Authentication
   - Connection pooling
   - Statement caching
   - Proper error handling
   - Comprehensive logging

## License

Apache License 2.0