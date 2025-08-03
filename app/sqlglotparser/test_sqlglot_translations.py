"""
Test cases for SQLGlot SQL translation functionality.
"""

import pytest
from snowflake_proxy.sqlglotparser.sqlglot_parser import SQLGlotParser


def test_translate_simple_select():
    """Test translating a simple SELECT query from Snowflake to PostgreSQL."""
    parser = SQLGlotParser()
    snowflake_query = "SELECT column1, column2 FROM my_table WHERE column1 > 0;"

    result = parser.parse(snowflake_query, target_dialect="postgres")

    assert result["success"], "Query should be parsed successfully"
    assert result["translated_sql"] is not None, "Translated SQL should not be None"

    # The translated query should be valid PostgreSQL but functionally equivalent
    expected = "SELECT column1, column2 FROM my_table WHERE column1 > 0"
    assert result["translated_sql"].lower() == expected.lower(), (
        "Translation should match expected PostgreSQL"
    )


def test_translate_snowflake_specific_functions():
    """Test translating Snowflake-specific functions to PostgreSQL equivalents."""
    parser = SQLGlotParser()
    snowflake_query = """
    SELECT 
        DATEADD(day, 1, current_date()),
        TO_VARCHAR(column1, 'YYYY-MM-DD'),
        NVL(nullable_col, 'default')
    FROM my_table;
    """

    result = parser.parse(snowflake_query, target_dialect="postgres")
    assert result["success"], "Query should be parsed successfully"
    assert result["translated_sql"] is not None, "Translated SQL should not be None"

    # Verify that Snowflake functions are translated to PostgreSQL equivalents
    translated = result["translated_sql"].lower()
    assert "current_date" in translated, "Should translate current_date() function"
    assert "coalesce" in translated, "Should translate NVL to COALESCE"
    assert "to_char" in translated, "Should translate TO_VARCHAR to TO_CHAR"


def test_translate_invalid_query():
    """Test that invalid SQL raises appropriate parsing error."""
    parser = SQLGlotParser()
    invalid_query = "SELECT * FORM my_table;"  # FORM is misspelled

    with pytest.raises(Exception):
        parser.parse(invalid_query, target_dialect="postgres")


def test_translate_complex_select():
    """Test translating a simple SELECT query from Snowflake to PostgreSQL."""
    parser = SQLGlotParser()
    snowflake_query = """
        WITH daily_stats AS (
    SELECT 
        DATE_TRUNC('day', event_timestamp) as event_date,
        user_id,
        PARSE_JSON(event_data):user_agent::STRING as user_agent,  -- Snowflake JSON access
        COUNT(*) as event_count,
        IFF(ARRAY_SIZE(SPLIT(user_agent, ' ')) > 2, TRUE, FALSE) as is_complex_agent,  -- Snowflake functions
        LAG(event_count, 1, 0) OVER (PARTITION BY user_id ORDER BY event_date) as prev_day_count,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_count DESC) as rank
    FROM raw_events
    WHERE event_timestamp >= DATEADD('day', -7, CURRENT_TIMESTAMP())  -- Snowflake date arithmetic
    QUALIFY rank <= 3  -- Snowflake-specific QUALIFY clause
)
SELECT 
    event_date,
    user_id,
    user_agent,
    event_count,
    ZEROIFNULL(prev_day_count) as prev_day_count,  -- Snowflake NULL handling
    CASE 
        WHEN event_count > NVL(prev_day_count, 0) THEN 'Increased'  -- Snowflake NVL function
        WHEN event_count < NVL(prev_day_count, 0) THEN 'Decreased'
        ELSE 'No Change'
    END as trend
FROM daily_stats
WHERE is_complex_agent = TRUE
ORDER BY event_date DESC, event_count DESC;
        """

    result = parser.parse(snowflake_query, target_dialect="postgres")

    assert result["success"], "Query should be parsed successfully"
    assert result["translated_sql"] is not None, "Translated SQL should not be None"

    with open("translated_query.sql", "w") as f:
        f.write(result["translated_sql"])

    # The translated query should be valid PostgreSQL but functionally equivalent
    expected = "WITH daily_stats AS (SELECT event_date, user_id, user_agent, event_count, is_complex_agent, prev_day_count, rank FROM (SELECT DATE_TRUNC('DAY', event_timestamp) AS event_date, user_id, CAST(JSON_EXTRACT_PATH(CAST(event_data AS JSON), 'user_agent') AS TEXT) AS user_agent /* Snowflake JSON access */, COUNT(*) AS event_count, CASE WHEN ARRAY_LENGTH(SPLIT(user_agent, ' '), 1) > 2 THEN TRUE ELSE FALSE END AS is_complex_agent /* Snowflake functions */, LAG(event_count, 1, 0) OVER (PARTITION BY user_id ORDER BY event_date) AS prev_day_count, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_count DESC) AS rank FROM raw_events WHERE event_timestamp >= CURRENT_TIMESTAMP + INTERVAL '-7 DAY' /* Snowflake date arithmetic */) AS _t WHERE rank <= 3 /* Snowflake-specific QUALIFY clause */) SELECT event_date, user_id, user_agent, event_count, CASE WHEN prev_day_count IS NULL THEN 0 ELSE prev_day_count END AS prev_day_count /* Snowflake NULL handling */, CASE WHEN event_count > COALESCE(prev_day_count, 0) THEN 'Increased' /* Snowflake NVL function */ WHEN event_count < COALESCE(prev_day_count, 0) THEN 'Decreased' ELSE 'No Change' END AS trend FROM daily_stats WHERE is_complex_agent = TRUE ORDER BY event_date DESC, event_count DESC"
    assert result["translated_sql"].lower() == expected.lower(), (
        "Translation should match expected PostgreSQL"
    )
