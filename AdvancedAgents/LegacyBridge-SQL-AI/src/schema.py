"""Schema inspection and formatting utilities.

This module provides utilities for formatting database schema information
in a way that's useful for LLMs to understand the database structure.
"""

from typing import Any


def format_column_definition(column: dict[str, Any]) -> str:
    """Format a single column definition for display.
    
    Args:
        column: Column metadata from PRAGMA table_info
        
    Returns:
        Formatted column string
    """
    parts = [f"{column['name']}: {column['type']}"]
    
    if column["notnull"]:
        parts.append("NOT NULL")
    
    if column["pk"]:
        parts.append("PRIMARY KEY")
    
    if column["dflt_value"] is not None:
        parts.append(f"DEFAULT {column['dflt_value']}")
    
    return " ".join(parts)


def format_table_schema(table_name: str, columns: list[dict[str, Any]]) -> str:
    """Format a table schema for display.
    
    Args:
        table_name: Name of the table
        columns: List of column definitions
        
    Returns:
        Formatted schema as a multi-line string
    """
    lines = [f"Table: {table_name}", "=" * (7 + len(table_name)), ""]
    
    for column in columns:
        lines.append(f"  • {format_column_definition(column)}")
    
    return "\n".join(lines)


def format_full_schema(schema: dict[str, list[dict[str, Any]]]) -> str:
    """Format the complete database schema.
    
    Args:
        schema: Dictionary mapping table names to column definitions
        
    Returns:
        Formatted schema as a multi-line string
    """
    sections = []
    
    for table_name, columns in sorted(schema.items()):
        sections.append(format_table_schema(table_name, columns))
    
    return "\n\n".join(sections)


def get_schema_summary(schema: dict[str, list[dict[str, Any]]]) -> str:
    """Get a brief summary of the database schema.
    
    Args:
        schema: Dictionary mapping table names to column definitions
        
    Returns:
        Brief summary string
    """
    table_summaries = []
    
    for table_name, columns in sorted(schema.items()):
        column_names = [col["name"] for col in columns]
        pk_columns = [col["name"] for col in columns if col["pk"]]
        
        summary = f"{table_name} ({len(columns)} columns"
        if pk_columns:
            summary += f", PK: {', '.join(pk_columns)}"
        summary += ")"
        
        table_summaries.append(summary)
    
    return "\n".join(table_summaries)


def get_table_relationships(schema: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Infer table relationships based on naming conventions.
    
    This function looks for foreign key patterns in column names
    (e.g., ArtistId, CustomerId) to suggest relationships.
    
    Args:
        schema: Dictionary mapping table names to column definitions
        
    Returns:
        List of relationship descriptions
    """
    relationships = []
    
    # Look for columns that end with "Id" and match table names
    for table_name, columns in schema.items():
        for column in columns:
            col_name = column["name"]
            
            # Check if column name ends with "Id" and is not the primary key
            if col_name.endswith("Id") and not column["pk"]:
                # Try to find matching table name
                potential_table = col_name[:-2]  # Remove "Id" suffix
                
                # Check if this table exists (case-insensitive)
                for other_table in schema.keys():
                    if other_table.lower() == potential_table.lower():
                        relationships.append(
                            f"{table_name}.{col_name} -> {other_table}.{other_table}Id"
                        )
                        break
    
    return relationships


def create_llm_context(schema: dict[str, list[dict[str, Any]]]) -> str:
    """Create a comprehensive context string for LLMs.
    
    This provides all the information an LLM needs to understand
    the database structure and write queries.
    
    Args:
        schema: Dictionary mapping table names to column definitions
        
    Returns:
        Formatted context string for LLMs
    """
    sections = [
        "# Database Schema: Chinook Digital Media Store",
        "",
        "## Overview",
        f"This database contains {len(schema)} tables representing a digital media store.",
        "",
        "## Tables Summary",
        get_schema_summary(schema),
        "",
        "## Detailed Schema",
        format_full_schema(schema),
    ]
    
    # Add relationships if found
    relationships = get_table_relationships(schema)
    if relationships:
        sections.extend([
            "",
            "## Inferred Relationships",
            "\n".join(f"  • {rel}" for rel in relationships)
        ])
    
    return "\n".join(sections)
