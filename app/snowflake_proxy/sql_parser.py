from lark import Lark, Transformer, v_args
import logging

logger = logging.getLogger(__name__)

# Snowflake CREATE TABLE grammar in Lark format
SNOWFLAKE_CREATE_TABLE_GRAMMAR = """
    ?start: create_table_stmt

    create_table_stmt: "CREATE" or_replace? table_type? "TABLE" if_not_exists? table_name 
                      (column_clause | as_query)

    or_replace: "OR" "REPLACE"
    
    table_type: ("LOCAL" | "GLOBAL")? ("TEMP" | "TEMPORARY" | "VOLATILE" | "TRANSIENT")
    
    if_not_exists: "IF" "NOT" "EXISTS"
    
    table_name: IDENTIFIER ("." IDENTIFIER)*
    
    column_clause: "(" column_list out_of_line_constraints? ")" table_options*
    
    as_query: table_options* "AS" query
    
    query: /SELECT .*/  // Simplified for now, should be expanded for full SQL parsing
    
    column_list: column_def ("," column_def)*
    
    column_def: column_name data_type column_options*
    
    column_name: IDENTIFIER
    
    data_type: IDENTIFIER ("(" (NUMBER | "MAX") ("," NUMBER)* ")")? 
    
    column_options: inline_constraint
                 | not_null
                 | collate
                 | default_value
                 | autoincrement
                 | masking_policy
                 | projection_policy
                 | tag
                 | comment

    inline_constraint: "CONSTRAINT" IDENTIFIER? constraint_type
    
    constraint_type: "UNIQUE"
                  | "PRIMARY" "KEY"
                  | "FOREIGN" "KEY" "REFERENCES" table_name "(" column_list ")"
                  | "CHECK" "(" expr ")"
    
    out_of_line_constraints: "," constraint ("," constraint)*
    
    constraint: "CONSTRAINT" IDENTIFIER? constraint_type
    
    not_null: "NOT" "NULL"
    
    collate: "COLLATE" STRING
    
    default_value: "DEFAULT" expr
    
    autoincrement: ("AUTOINCREMENT" | "IDENTITY") 
                   ("(" NUMBER "," NUMBER ")" | "START" NUMBER "INCREMENT" NUMBER)?
                   ("ORDER" | "NOORDER")?
    
    masking_policy: "WITH"? "MASKING" "POLICY" IDENTIFIER ("USING" "(" column_list ")")?
    
    projection_policy: "WITH"? "PROJECTION" "POLICY" IDENTIFIER
    
    tag: "WITH"? "TAG" "(" tag_list ")"
    
    tag_list: tag_item ("," tag_item)*
    
    tag_item: IDENTIFIER "=" STRING
    
    comment: "COMMENT" STRING
    
    table_options: cluster_by
                | schema_evolution
                | data_retention
                | data_extension
                | change_tracking
                | ddl_collation
                | copy_grants
                | table_comment
                | row_access_policy
                | aggregation_policy
                | join_policy
                | table_tag
                | contact

    cluster_by: "CLUSTER" "BY" "(" expr_list ")"
    
    schema_evolution: "ENABLE_SCHEMA_EVOLUTION" "=" BOOLEAN
    
    data_retention: "DATA_RETENTION_TIME_IN_DAYS" "=" NUMBER
    
    data_extension: "MAX_DATA_EXTENSION_TIME_IN_DAYS" "=" NUMBER
    
    change_tracking: "CHANGE_TRACKING" "=" BOOLEAN
    
    ddl_collation: "DEFAULT_DDL_COLLATION" "=" STRING
    
    copy_grants: "COPY" "GRANTS"
    
    table_comment: "COMMENT" "=" STRING
    
    row_access_policy: "WITH"? "ROW" "ACCESS" "POLICY" IDENTIFIER "ON" "(" column_list ")"
    
    aggregation_policy: "WITH"? "AGGREGATION" "POLICY" IDENTIFIER ("ENTITY" "KEY" "(" column_list ")")?
    
    join_policy: "WITH"? "JOIN" "POLICY" IDENTIFIER ("ALLOWED" "JOIN" "KEYS" "(" column_list ")")?
    
    table_tag: "WITH"? "TAG" "(" tag_list ")"
    
    contact: "WITH" "CONTACT" "(" contact_list ")"
    
    contact_list: contact_item ("," contact_item)*
    
    contact_item: IDENTIFIER "=" IDENTIFIER
    
    expr_list: expr ("," expr)*
    
    expr: function_call
        | arithmetic_expr
        | comparison_expr
        | literal
        | column_ref
        | "(" expr ")"

    function_call: IDENTIFIER "(" (expr ("," expr)*)? ")"
    
    arithmetic_expr: expr operator expr
    
    comparison_expr: expr comp_operator expr
    
    operator: "+" | "-" | "*" | "/" | "%"
    
    comp_operator: "=" | "!=" | "<>" | "<" | "<=" | ">" | ">="
    
    column_ref: IDENTIFIER ("." IDENTIFIER)*
    
    literal: NUMBER | STRING | BOOLEAN | "NULL"
    
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /-?[0-9]+(\.[0-9]+)?/
    BOOLEAN: "TRUE" | "FALSE"
    STRING: /'[^']*'/
    
    %import common.WS
    %import common.ESCAPED_STRING
    %ignore WS
"""

class SnowflakeParser:
    def __init__(self):
        self.parser = Lark(SNOWFLAKE_CREATE_TABLE_GRAMMAR, parser='lalr', debug=True)
        
    def parse_create_table(self, sql: str) -> bool:
        """
        Parse a CREATE TABLE statement and validate its syntax.
        
        Args:
            sql: The SQL statement to parse
            
        Returns:
            bool: True if the syntax is valid, False otherwise
            
        Raises:
            lark.exceptions.UnexpectedInput: If the syntax is invalid
        """
        try:
            tree = self.parser.parse(sql)
            logger.debug(f"Successfully parsed SQL: {sql}")
            logger.debug(f"Parse tree: {tree.pretty()}")
            return True
        except Exception as e:
            logger.error(f"Failed to parse SQL: {sql}")
            logger.error(f"Error: {str(e)}")
            raise

    def validate_sql(self, sql: str) -> bool:
        """
        Validate any supported SQL statement.
        Currently only supports CREATE TABLE statements.
        
        Args:
            sql: The SQL statement to validate
            
        Returns:
            bool: True if the syntax is valid, False otherwise
        """
        sql = sql.strip()
        
        if sql.upper().startswith("CREATE TABLE"):
            return self.parse_create_table(sql)
        else:
            raise NotImplementedError("Only CREATE TABLE statements are currently supported")