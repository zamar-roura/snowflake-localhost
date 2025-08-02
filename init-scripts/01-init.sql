-- Initialize PostgreSQL database for Snowflake localhost proxy

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create a schema for Snowflake-like objects
CREATE SCHEMA IF NOT EXISTS public;

-- Create a function to generate UUIDs (similar to Snowflake's UUID_STRING())
CREATE OR REPLACE FUNCTION generate_uuid()
RETURNS TEXT AS $$
BEGIN
    RETURN uuid_generate_v4()::text;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get current timestamp (similar to Snowflake's CURRENT_TIMESTAMP())
CREATE OR REPLACE FUNCTION current_timestamp_snowflake()
RETURNS TIMESTAMP AS $$
BEGIN
    RETURN CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get current date (similar to Snowflake's CURRENT_DATE())
CREATE OR REPLACE FUNCTION current_date_snowflake()
RETURNS DATE AS $$
BEGIN
    RETURN CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Set default search path
SET search_path TO public;

-- Create some example tables for testing
CREATE TABLE IF NOT EXISTS example_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample data
INSERT INTO example_table (name) VALUES 
    ('Sample Record 1'),
    ('Sample Record 2'),
    ('Sample Record 3')
ON CONFLICT DO NOTHING;

-- Create a view for testing
CREATE OR REPLACE VIEW example_view AS
SELECT id, name, created_at FROM example_table;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO snowflake_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO snowflake_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO snowflake_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO snowflake_user; 