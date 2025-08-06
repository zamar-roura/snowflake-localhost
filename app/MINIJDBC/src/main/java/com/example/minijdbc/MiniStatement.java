package com.example.minijdbc;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.sql.*;
import java.util.HashMap;
import java.util.Map;

public class MiniStatement implements Statement {
    private final MiniConnection connection;
    private final CloseableHttpClient httpClient;
    private final String endpoint;
    private final ObjectMapper objectMapper;
    private boolean isClosed = false;
    private ResultSet currentResultSet = null;

    public MiniStatement(MiniConnection connection, CloseableHttpClient httpClient, String endpoint) {
        this.connection = connection;
        this.httpClient = httpClient;
        this.endpoint = endpoint;
        this.objectMapper = new ObjectMapper();
    }

    @Override
    public ResultSet executeQuery(String sql) throws SQLException {
        if (execute(sql)) {
            return currentResultSet;
        }
        throw new SQLException("The query did not produce a result set");
    }

    @Override
    public boolean execute(String sql) throws SQLException {
        checkClosed();
        
        try {
            // Create the request payload
            Map<String, Object> payload = new HashMap<>();
            payload.put("query", sql);
            payload.put("connection_id", ((MiniConnection)connection).getConnectionId());
            String jsonPayload = objectMapper.writeValueAsString(payload);

            // Create HTTP POST request
            HttpPost httpPost = new HttpPost(endpoint + "/v1/query");
            httpPost.setHeader("Content-Type", "application/json");
            httpPost.setEntity(new StringEntity(jsonPayload));

            // Execute the request
            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                String responseBody = EntityUtils.toString(response.getEntity());
                
                // Check response status
                int statusCode = response.getStatusLine().getStatusCode();
                if (statusCode != 200) {
                    throw new SQLException("Request failed with status: " + statusCode + ", body: " + responseBody);
                }

                // Parse the response
                Map<String, Object> result = objectMapper.readValue(responseBody, Map.class);
                
                // Check for errors
                if (!((Boolean)result.get("success"))) {
                    throw new SQLException(result.get("error").toString());
                }

                // Handle the result
                if (result.containsKey("result")) {
                    // Create a ResultSet from the data
                    currentResultSet = new MiniResultSet(result.get("result"));
                    return true;
                } else {
                    // For DDL/DML operations that don't return results
                    currentResultSet = null;
                    return false;
                }
            }
        } catch (IOException e) {
            throw new SQLException("Failed to execute statement", e);
        }
    }

    @Override
    public int executeUpdate(String sql) throws SQLException {
        checkClosed();
        
        try {
            // Create the request payload
            Map<String, Object> payload = new HashMap<>();
            payload.put("sql", sql);
            String jsonPayload = objectMapper.writeValueAsString(payload);

            // Create HTTP POST request
            HttpPost httpPost = new HttpPost(endpoint + "/execute");
            httpPost.setHeader("Content-Type", "application/json");
            httpPost.setEntity(new StringEntity(jsonPayload));

            // Execute the request
            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                String responseBody = EntityUtils.toString(response.getEntity());
                
                // Check response status
                int statusCode = response.getStatusLine().getStatusCode();
                if (statusCode != 200) {
                    throw new SQLException("Request failed with status: " + statusCode + ", body: " + responseBody);
                }

                // Parse the response
                Map<String, Object> result = objectMapper.readValue(responseBody, Map.class);
                
                // Check for errors
                if (result.containsKey("error")) {
                    throw new SQLException(result.get("error").toString());
                }

                // Return update count
                return result.containsKey("updateCount") ? 
                    ((Number) result.get("updateCount")).intValue() : 0;
            }
        } catch (IOException e) {
            throw new SQLException("Failed to execute update", e);
        }
    }

    @Override
    public void close() throws SQLException {
        if (!isClosed) {
            if (currentResultSet != null) {
                currentResultSet.close();
                currentResultSet = null;
            }
            isClosed = true;
        }
    }

    @Override
    public boolean isClosed() throws SQLException {
        return isClosed;
    }

    private void checkClosed() throws SQLException {
        if (isClosed) {
            throw new SQLException("Statement is closed");
        }
    }

    // Required JDBC methods with minimal implementation
    @Override
    public int getMaxFieldSize() throws SQLException {
        return 0;
    }

    @Override
    public void setMaxFieldSize(int max) throws SQLException {
        // No-op
    }

    @Override
    public int getMaxRows() throws SQLException {
        return 0;
    }

    @Override
    public void setMaxRows(int max) throws SQLException {
        // No-op
    }

    @Override
    public void setEscapeProcessing(boolean enable) throws SQLException {
        // No-op
    }

    @Override
    public int getQueryTimeout() throws SQLException {
        return 0;
    }

    @Override
    public void setQueryTimeout(int seconds) throws SQLException {
        // No-op
    }

    @Override
    public void cancel() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public SQLWarning getWarnings() throws SQLException {
        return null;
    }

    @Override
    public void clearWarnings() throws SQLException {
        // No-op
    }

    @Override
    public void setCursorName(String name) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public ResultSet getResultSet() throws SQLException {
        return currentResultSet;
    }

    @Override
    public int getUpdateCount() throws SQLException {
        return -1;
    }

    @Override
    public boolean getMoreResults() throws SQLException {
        return false;
    }

    // Add remaining JDBC interface methods with throw new SQLFeatureNotSupportedException()
    @Override
    public void setFetchDirection(int direction) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int getFetchDirection() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void setFetchSize(int rows) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int getFetchSize() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int getResultSetConcurrency() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int getResultSetType() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void addBatch(String sql) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void clearBatch() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int[] executeBatch() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public Connection getConnection() throws SQLException {
        return connection;
    }

    @Override
    public boolean getMoreResults(int current) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public ResultSet getGeneratedKeys() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int executeUpdate(String sql, int autoGeneratedKeys) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int executeUpdate(String sql, int[] columnIndexes) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int executeUpdate(String sql, String[] columnNames) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public boolean execute(String sql, int autoGeneratedKeys) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public boolean execute(String sql, int[] columnIndexes) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public boolean execute(String sql, String[] columnNames) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int getResultSetHoldability() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public boolean isPoolable() throws SQLException {
        return false;
    }

    @Override
    public void setPoolable(boolean poolable) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void closeOnCompletion() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public boolean isCloseOnCompletion() throws SQLException {
        return false;
    }

    @Override
    public <T> T unwrap(Class<T> iface) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public boolean isWrapperFor(Class<?> iface) throws SQLException {
        return false;
    }
}