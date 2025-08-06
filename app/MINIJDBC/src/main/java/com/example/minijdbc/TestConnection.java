package com.example.minijdbc;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class TestConnection {
    public static void main(String[] args) {
        try {
            // Register the driver (optional as it auto-registers)
            Class.forName("com.example.minijdbc.MiniDriver");

            // Connection properties
            Properties props = new Properties();
            props.setProperty("user", "your_username");
            props.setProperty("password", "your_password");
            props.setProperty("database", "your_database");
            props.setProperty("schema", "public");

            // Create connection
            String url = "jdbc:flaskdb://localhost:4566";
            System.out.println("Connecting to: " + url);
            
            Connection conn = DriverManager.getConnection(url, props);
            System.out.println("Connected successfully!");

            // Test a simple query
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT 1 as test");
            
            while (rs.next()) {
                System.out.println("Test query result: " + rs.getInt("test"));
            }

            // Close resources
            rs.close();
            stmt.close();
            conn.close();
            System.out.println("Connection closed successfully!");

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}