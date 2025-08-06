package com.example.minijdbc;

import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.entity.StringEntity;
import org.apache.http.util.EntityUtils;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.sql.*;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.Executor;

public class MiniConnection implements Connection {
    private final String url;
    private final Properties properties;
    private boolean isClosed = false;
    private final CloseableHttpClient httpClient;
    private final String endpoint;
    private final String connectionId;

    public MiniConnection(String url, Properties info) throws SQLException {
        this.url = url;
        this.properties = info;
        this.httpClient = HttpClients.createDefault();
        
        // Parse URL to get endpoint
        // Format: jdbc:flaskdb://hostname:port
        try {
            String urlWithoutPrefix = url.substring("jdbc:flaskdb://".length());
            this.endpoint = "http://" + urlWithoutPrefix;
            this.connectionId = createConnection();
        } catch (Exception e) {
            throw new SQLException("Invalid URL format. Expected: jdbc:flaskdb://hostname:port", e);
        }
    }

    private String createConnection() throws SQLException {
        try {
            HttpPost request = new HttpPost(endpoint + "/v1/connection");
            request.setHeader("Content-Type", "application/json");

            // Create connection request body
            JsonObject json = new JsonObject();
            json.addProperty("user", properties.getProperty("user"));
            json.addProperty("password", properties.getProperty("password"));
            json.addProperty("database", properties.getProperty("database"));
            json.addProperty("schema", properties.getProperty("schema"));

            StringEntity entity = new StringEntity(json.toString());
            request.setEntity(entity);

            try (CloseableHttpResponse response = httpClient.execute(request)) {
                String responseBody = EntityUtils.toString(response.getEntity());
                JsonObject responseJson = JsonParser.parseString(responseBody).getAsJsonObject();

                if (!responseJson.get("success").getAsBoolean()) {
                    throw new SQLException(responseJson.get("error").getAsString());
                }

                return responseJson.get("connection_id").getAsString();
            }
        } catch (Exception e) {
            throw new SQLException("Failed to create connection: " + e.getMessage(), e);
        }
    }

    @Override
    public Statement createStatement() throws SQLException {
        checkClosed();
        return new MiniStatement(this, httpClient, endpoint);
    }

    public String getConnectionId() {
        return connectionId;
    }

    @Override
    public void close() throws SQLException {
        if (!isClosed) {
            try {
                // Close the Flask connection
                HttpDelete request = new HttpDelete(endpoint + "/v1/connection/" + connectionId);
                try (CloseableHttpResponse response = httpClient.execute(request)) {
                    String responseBody = EntityUtils.toString(response.getEntity());
                    JsonObject responseJson = JsonParser.parseString(responseBody).getAsJsonObject();
                    if (!responseJson.get("success").getAsBoolean()) {
                        throw new SQLException(responseJson.get("error").getAsString());
                    }
                }

                // Close the HTTP client
                httpClient.close();
            } catch (Exception e) {
                throw new SQLException("Error closing connection: " + e.getMessage(), e);
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
            throw new SQLException("Connection is closed");
        }
    }

    // Required JDBC methods with minimal implementation
    @Override
    public boolean isValid(int timeout) throws SQLException {
        return !isClosed;
    }

    @Override
    public void setAutoCommit(boolean autoCommit) throws SQLException {
        // No-op for this simple implementation
    }

    @Override
    public boolean getAutoCommit() throws SQLException {
        return true;
    }

    // Other required methods with default implementation
    @Override
    public PreparedStatement prepareStatement(String sql) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public CallableStatement prepareCall(String sql) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public String nativeSQL(String sql) throws SQLException {
        return sql;
    }

    @Override
    public void commit() throws SQLException {
        // No-op for this simple implementation
    }

    @Override
    public void rollback() throws SQLException {
        // No-op for this simple implementation
    }

    @Override
    public DatabaseMetaData getMetaData() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void setReadOnly(boolean readOnly) throws SQLException {
        // No-op for this simple implementation
    }

    @Override
    public boolean isReadOnly() throws SQLException {
        return false;
    }

    @Override
    public void setCatalog(String catalog) throws SQLException {
        // No-op for this simple implementation
    }

    @Override
    public String getCatalog() throws SQLException {
        return null;
    }

    @Override
    public void setTransactionIsolation(int level) throws SQLException {
        // No-op for this simple implementation
    }

    @Override
    public int getTransactionIsolation() throws SQLException {
        return Connection.TRANSACTION_NONE;
    }

    @Override
    public SQLWarning getWarnings() throws SQLException {
        return null;
    }

    @Override
    public void clearWarnings() throws SQLException {
        // No-op for this simple implementation
    }

    // Add remaining JDBC interface methods with throw new SQLFeatureNotSupportedException()
    // This is just a subset of the required methods for brevity
    @Override
    public Map<String, Class<?>> getTypeMap() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void setTypeMap(Map<String, Class<?>> map) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void setHoldability(int holdability) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int getHoldability() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public Savepoint setSavepoint() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public Savepoint setSavepoint(String name) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void rollback(Savepoint savepoint) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void releaseSavepoint(Savepoint savepoint) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public Statement createStatement(int resultSetType, int resultSetConcurrency) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public PreparedStatement prepareStatement(String sql, int resultSetType, int resultSetConcurrency)
            throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public CallableStatement prepareCall(String sql, int resultSetType, int resultSetConcurrency)
            throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public Statement createStatement(int resultSetType, int resultSetConcurrency, int resultSetHoldability)
            throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public PreparedStatement prepareStatement(String sql, int resultSetType, int resultSetConcurrency,
            int resultSetHoldability) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public CallableStatement prepareCall(String sql, int resultSetType, int resultSetConcurrency,
            int resultSetHoldability) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public PreparedStatement prepareStatement(String sql, int autoGeneratedKeys) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public PreparedStatement prepareStatement(String sql, int[] columnIndexes) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public PreparedStatement prepareStatement(String sql, String[] columnNames) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public Clob createClob() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public Blob createBlob() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public NClob createNClob() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public SQLXML createSQLXML() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void setSchema(String schema) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public String getSchema() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void abort(Executor executor) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public void setNetworkTimeout(Executor executor, int milliseconds) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public int getNetworkTimeout() throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public <T> T unwrap(Class<T> iface) throws SQLException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public boolean isWrapperFor(Class<?> iface) throws SQLException {
        return false;
    }

    @Override
    public Struct createStruct(String typeName, Object[] attributes) throws SQLException {
        throw new SQLFeatureNotSupportedException("createStruct not supported");
    }

    @Override
    public Array createArrayOf(String typeName, Object[] elements) throws SQLException {
        throw new SQLFeatureNotSupportedException("createArrayOf not supported");
    }

    @Override
    public Properties getClientInfo() throws SQLException {
        return new Properties();
    }

    @Override
    public String getClientInfo(String name) throws SQLException {
        return null;
    }

    @Override
    public void setClientInfo(Properties properties) throws SQLClientInfoException {
        // No-op
    }

    @Override
    public void setClientInfo(String name, String value) throws SQLClientInfoException {
        // No-op
    }
}