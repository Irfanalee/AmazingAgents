"""MCP Server for Legacy Bridge SQL AI.

This server exposes the Chinook database to LLMs via the Model Context Protocol,
allowing natural language queries to be converted to SQL and executed safely.
"""

import asyncio
import json
import logging
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

from .database import DatabaseManager
from .schema import create_llm_context, format_table_schema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("legacy-bridge")


class LegacyBridgeServer:
    """MCP Server for querying legacy databases."""

    def __init__(self, db_path: Path | str, pool_size: int = 5):
        """Initialize the server with connection pooling.

        Args:
            db_path: Path to the SQLite database
            pool_size: Maximum number of database connections in pool (default: 5)
        """
        self.db = DatabaseManager(db_path, pool_size=pool_size)
        self.server = Server("legacy-bridge-sql-ai")

        # Register handlers
        self._register_handlers()

        logger.info(f"Legacy Bridge server initialized with database: {db_path}")
        logger.info(f"Connection pool size: {pool_size}")
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources():
            """List available database schema resources."""
            resources = [
                Resource(
                    uri="schema://database",
                    name="Complete Database Schema",
                    description="Full schema of the Chinook database with all tables and columns",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="schema://tables",
                    name="Table List",
                    description="List of all tables in the database",
                    mimeType="application/json"
                )
            ]
            
            # Add resource for each table
            for table in self.db.get_tables():
                resources.append(
                    Resource(
                        uri=f"schema://table/{table}",
                        name=f"Schema: {table}",
                        description=f"Schema definition for the {table} table",
                        mimeType="text/plain"
                    )
                )
            
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str):
            """Read a database schema resource.
            
            Args:
                uri: Resource URI (e.g., schema://database, schema://table/Artist)
            """
            logger.info(f"Reading resource: {uri}")
            
            if uri == "schema://database":
                # Return full database schema
                schema = self.db.get_full_schema()
                content = create_llm_context(schema)
                return TextContent(
                    type="text",
                    text=content
                )
            
            elif uri == "schema://tables":
                # Return list of tables as JSON
                tables = self.db.get_tables()
                return TextContent(
                    type="text",
                    text=json.dumps(tables, indent=2)
                )
            
            elif uri.startswith("schema://table/"):
                # Return specific table schema
                table_name = uri.replace("schema://table/", "")
                columns = self.db.get_table_schema(table_name)
                content = format_table_schema(table_name, columns)
                return TextContent(
                    type="text",
                    text=content
                )
            
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
        
        @self.server.list_tools()
        async def list_tools():
            """List available tools."""
            return [
                Tool(
                    name="query_database",
                    description=(
                        "Execute a read-only SQL query against the Chinook database. "
                        "Only SELECT queries are allowed. Returns results as JSON. "
                        "Use this tool to answer questions about customers, artists, "
                        "albums, tracks, invoices, and sales data."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sql": {
                                "type": "string",
                                "description": "The SQL SELECT query to execute"
                            }
                        },
                        "required": ["sql"]
                    }
                ),
                Tool(
                    name="get_table_schema",
                    description=(
                        "Get the schema (column definitions) for a specific table. "
                        "Use this to understand table structure before writing queries."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to inspect"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                Tool(
                    name="get_database_stats",
                    description=(
                        "Get statistics about the database including table counts, "
                        "row counts, and column counts. Useful for understanding "
                        "the database size and scope."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Execute a tool.
            
            Args:
                name: Tool name
                arguments: Tool arguments
            """
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            try:
                if name == "query_database":
                    sql = arguments.get("sql")
                    if not sql:
                        raise ValueError("Missing required argument: sql")
                    
                    results = self.db.execute_query(sql)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "rows": results,
                            "count": len(results)
                        }, indent=2)
                    )]
                
                elif name == "get_table_schema":
                    table_name = arguments.get("table_name")
                    if not table_name:
                        raise ValueError("Missing required argument: table_name")
                    
                    columns = self.db.get_table_schema(table_name)
                    content = format_table_schema(table_name, columns)
                    
                    return [TextContent(
                        type="text",
                        text=content
                    )]
                
                elif name == "get_database_stats":
                    stats = self.db.get_database_stats()
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(stats, indent=2)
                    )]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    }, indent=2)
                )]
    
    async def run(self):
        """Run the MCP server."""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        finally:
            # Cleanup database connections
            logger.info("Shutting down database connections...")
            self.db.close()


def get_database_path() -> Path:
    """Get the path to the Chinook database.
    
    Returns:
        Path to the database file
        
    Raises:
        FileNotFoundError: If database file doesn't exist
    """
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    db_path = project_root / "data" / "chinook.db"
    
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at: {db_path}\n"
            "Please download the Chinook database first (see README.md)"
        )
    
    return db_path


async def main():
    """Main entry point for the MCP server."""
    try:
        db_path = get_database_path()
        server = LegacyBridgeServer(db_path)
        logger.info("Starting Legacy Bridge MCP server...")
        await server.run()
    except FileNotFoundError as e:
        logger.error(str(e))
        exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
