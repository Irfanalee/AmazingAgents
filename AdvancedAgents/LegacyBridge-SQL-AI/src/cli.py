"""Command-line interface for Legacy Bridge SQL AI.

This CLI allows you to query the Chinook database directly from the terminal
without needing to integrate with Claude Desktop or other MCP clients.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


def get_database_path() -> Path:
    """Get the path to the Chinook database."""
    # Get the project root directory
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    db_path = project_root / "data" / "chinook.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("Please download the Chinook database first (see README.md)")
        sys.exit(1)
    
    return db_path


def execute_query(sql: str) -> list[dict[str, Any]]:
    """Execute a SQL query and return results as a list of dictionaries.
    
    Args:
        sql: SQL query to execute (must be a SELECT statement)
        
    Returns:
        List of rows as dictionaries
        
    Raises:
        ValueError: If query is not a SELECT statement
        sqlite3.Error: If query execution fails
    """
    # Validate read-only (only SELECT statements allowed)
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed (read-only mode)")
    
    db_path = get_database_path()
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Convert rows to list of dictionaries
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_all_tables() -> list[str]:
    """Get list of all tables in the database."""
    sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    results = execute_query(sql)
    return [row["name"] for row in results]


def get_table_schema(table_name: str) -> list[dict[str, Any]]:
    """Get schema information for a specific table."""
    sql = f"PRAGMA table_info({table_name})"
    db_path = get_database_path()
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def print_results(results: list[dict[str, Any]]) -> None:
    """Pretty print query results."""
    if not results:
        print("No results found.")
        return
    
    # Get column names from first row
    columns = list(results[0].keys())
    
    # Calculate column widths
    col_widths = {col: len(col) for col in columns}
    for row in results:
        for col in columns:
            value_str = str(row[col]) if row[col] is not None else "NULL"
            col_widths[col] = max(col_widths[col], len(value_str))
    
    # Print header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print("\n" + header)
    print("-" * len(header))
    
    # Print rows
    for row in results:
        row_str = " | ".join(
            str(row[col]).ljust(col_widths[col]) if row[col] is not None 
            else "NULL".ljust(col_widths[col])
            for col in columns
        )
        print(row_str)
    
    print(f"\n✅ {len(results)} row(s) returned\n")


def cmd_query(args: argparse.Namespace) -> None:
    """Execute a SQL query."""
    try:
        results = execute_query(args.sql)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_results(results)
            
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)


def cmd_tables(args: argparse.Namespace) -> None:
    """List all tables in the database."""
    try:
        tables = get_all_tables()
        print("\n📊 Tables in Chinook Database:\n")
        for table in tables:
            print(f"  • {table}")
        print(f"\n✅ {len(tables)} table(s) found\n")
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)


def cmd_schema(args: argparse.Namespace) -> None:
    """Show schema for a table or all tables."""
    try:
        if args.table:
            # Show schema for specific table
            schema = get_table_schema(args.table)
            print(f"\n📋 Schema for table: {args.table}\n")
            
            for col in schema:
                pk_marker = " 🔑 PRIMARY KEY" if col["pk"] else ""
                not_null = " NOT NULL" if col["notnull"] else ""
                print(f"  • {col['name']}: {col['type']}{not_null}{pk_marker}")
            
            print()
        else:
            # Show all tables and their columns
            tables = get_all_tables()
            print("\n📋 Database Schema:\n")
            
            for table in tables:
                print(f"📊 {table}")
                schema = get_table_schema(table)
                for col in schema:
                    pk_marker = " 🔑" if col["pk"] else ""
                    print(f"   • {col['name']}: {col['type']}{pk_marker}")
                print()
                
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Legacy Bridge SQL AI - Query the Chinook database from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query artists
  python -m src.cli query "SELECT * FROM Artist LIMIT 5"
  
  # List all tables
  python -m src.cli tables
  
  # Show schema for a specific table
  python -m src.cli schema --table Artist
  
  # Show schema for all tables
  python -m src.cli schema
  
  # Get JSON output
  python -m src.cli query "SELECT * FROM Genre" --json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Execute a SQL query")
    query_parser.add_argument("sql", help="SQL query to execute (SELECT only)")
    query_parser.add_argument("--json", action="store_true", help="Output as JSON")
    query_parser.set_defaults(func=cmd_query)
    
    # Tables command
    tables_parser = subparsers.add_parser("tables", help="List all tables")
    tables_parser.set_defaults(func=cmd_tables)
    
    # Schema command
    schema_parser = subparsers.add_parser("schema", help="Show table schema")
    schema_parser.add_argument("--table", help="Specific table name (optional)")
    schema_parser.set_defaults(func=cmd_schema)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the command
    args.func(args)


if __name__ == "__main__":
    main()
