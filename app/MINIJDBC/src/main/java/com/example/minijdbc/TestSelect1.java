package com.example.minijdbc;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class TestSelect1 {
    public static void main(String[] args) {
        try {
            // Register the driver
            Class.forName("com.example.minijdbc.MiniDriver");

            // Connection properties
            Properties props = new Properties();
            props.setProperty("user", "postgres");      // default PostgreSQL user
            props.setProperty("password", "postgres");  // default PostgreSQL password
            props.setProperty("database", "postgres");  // default PostgreSQL database
            props.setProperty("schema", "public");      // default schema

            // Create connection to Flask app
            String url = "jdbc:flaskdb://localhost:4566";
            System.out.println("Connecting to: " + url);
            
            Connection conn = DriverManager.getConnection(url, props);
            System.out.println("Connected successfully!");

            // Create and execute statement
            Statement stmt = conn.createStatement();
            System.out.println("Executing query: SELECT 1 as test_column");
            ResultSet rs = stmt.executeQuery("SELECT 1 as test_column");
            
            // Print column names
            System.out.println("\nColumns in result set:");
            int columnCount = rs.getMetaData().getColumnCount();
            for (int i = 1; i <= columnCount; i++) {
                System.out.println("  - " + rs.getMetaData().getColumnName(i));
            }

            // Print results
            System.out.println("\nQuery results:");
            while (rs.next()) {
                System.out.println("test_column = " + rs.getInt("test_column"));
            }

            // Close resources
            rs.close();
            stmt.close();
            conn.close();
            System.out.println("\nConnection closed successfully!");

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}