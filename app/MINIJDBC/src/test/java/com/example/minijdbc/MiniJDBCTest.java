package com.example.minijdbc;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class MiniJDBCTest {
    private Connection connection;

    @Before
    public void setUp() throws Exception {
        // Register the driver
        Class.forName("com.example.minijdbc.MiniDriver");

        // Connection properties
        Properties props = new Properties();
        props.setProperty("user", "test_user");
        props.setProperty("password", "test_password");
        props.setProperty("database", "test_db");
        props.setProperty("schema", "public");

        // Create connection
        String url = "jdbc:flaskdb://localhost:4566";
        connection = DriverManager.getConnection(url, props);
    }

    @Test
    public void testSimpleSelect() throws Exception {
        // Create and execute statement
        Statement stmt = connection.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT 1 as test_value");

        // Verify we have a result
        assertTrue("ResultSet should have at least one row", rs.next());
        
        // Verify the value is 1
        assertEquals("SELECT 1 should return 1", 1, rs.getInt("test_value"));
        
        // Verify there are no more rows
        assertFalse("ResultSet should only have one row", rs.next());

        // Clean up
        rs.close();
        stmt.close();
    }

    @After
    public void tearDown() throws Exception {
        if (connection != null && !connection.isClosed()) {
            connection.close();
        }
    }
}