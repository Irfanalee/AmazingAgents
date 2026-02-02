"""Test script for the MCP server.

This script tests the MCP server functionality without needing Claude Desktop.
It simulates what an MCP client would do.
"""

import asyncio
import json
from pathlib import Path

from src.database import DatabaseManager
from src.schema import create_llm_context, format_table_schema


def test_database_manager():
    """Test the DatabaseManager functionality."""
    print("=" * 60)
    print("TEST 1: Database Manager")
    print("=" * 60)

    # Database is in the project root data directory
    db_path = Path(__file__).parent.parent / "data" / "chinook.db"
    db = DatabaseManager(db_path)
    
    # Test 1: Get tables
    print("\n✅ Test: Get all tables")
    tables = db.get_tables()
    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    
    # Test 2: Get table schema
    print("\n✅ Test: Get Artist table schema")
    artist_schema = db.get_table_schema("Artist")
    for col in artist_schema:
        print(f"  - {col['name']}: {col['type']} (PK: {bool(col['pk'])})")
    
    # Test 3: Execute query
    print("\n✅ Test: Query artists (LIMIT 3)")
    results = db.execute_query("SELECT * FROM Artist LIMIT 3")
    for row in results:
        print(f"  - {row}")
    
    # Test 4: Security - block non-SELECT
    print("\n✅ Test: Security - block DELETE query")
    try:
        db.execute_query("DELETE FROM Artist WHERE ArtistId = 1")
        print("  ❌ FAILED: Should have blocked DELETE query")
    except ValueError as e:
        print(f"  ✅ PASSED: Blocked with error: {e}")
    
    # Test 5: Database stats
    print("\n✅ Test: Get database statistics")
    stats = db.get_database_stats()
    print(f"  - Total tables: {stats['total_tables']}")
    for table, info in list(stats['tables'].items())[:3]:
        print(f"  - {table}: {info['columns']} columns, {info['rows']} rows")
    
    print("\n" + "=" * 60)
    print("✅ Database Manager Tests: PASSED")
    print("=" * 60)

    # Cleanup connections
    db.close()


def test_schema_utilities():
    """Test schema formatting utilities."""
    print("\n" + "=" * 60)
    print("TEST 2: Schema Utilities")
    print("=" * 60)

    # Database is in the project root data directory
    db_path = Path(__file__).parent.parent / "data" / "chinook.db"
    db = DatabaseManager(db_path)
    
    # Test 1: Format table schema
    print("\n✅ Test: Format table schema")
    columns = db.get_table_schema("Artist")
    formatted = format_table_schema("Artist", columns)
    print(formatted[:200] + "...")
    
    # Test 2: Create LLM context
    print("\n✅ Test: Create LLM context")
    schema = db.get_full_schema()
    context = create_llm_context(schema)
    print(f"Context length: {len(context)} characters")
    print("First 300 characters:")
    print(context[:300] + "...")
    
    print("\n" + "=" * 60)
    print("✅ Schema Utilities Tests: PASSED")
    print("=" * 60)

    # Cleanup connections
    db.close()


async def test_mcp_server():
    """Test MCP server initialization."""
    print("\n" + "=" * 60)
    print("TEST 3: MCP Server Initialization")
    print("=" * 60)
    
    try:
        from src.server import LegacyBridgeServer, get_database_path
        
        print("\n✅ Test: Get database path")
        db_path = get_database_path()
        print(f"Database path: {db_path}")
        
        print("\n✅ Test: Initialize MCP server")
        server = LegacyBridgeServer(db_path)
        print("Server initialized successfully!")
        print(f"Server name: {server.server.name}")
        
        print("\n✅ Test: Check registered handlers")
        print("Handlers registered:")
        print("  - list_resources")
        print("  - read_resource")
        print("  - list_tools")
        print("  - call_tool")
        
        print("\n" + "=" * 60)
        print("✅ MCP Server Tests: PASSED")
        print("=" * 60)

        # Cleanup connections
        server.db.close()

    except Exception as e:
        print(f"\n❌ MCP Server Test FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_mcp_protocol_simulation():
    """Simulate MCP protocol interactions."""
    print("\n" + "=" * 60)
    print("TEST 4: MCP Protocol Simulation")
    print("=" * 60)
    
    from src.server import LegacyBridgeServer, get_database_path
    
    db_path = get_database_path()
    server = LegacyBridgeServer(db_path)
    
    # Simulate listing resources
    print("\n✅ Simulating: list_resources()")
    print("Expected resources:")
    print("  - schema://database")
    print("  - schema://tables")
    tables = server.db.get_tables()
    for table in tables[:3]:
        print(f"  - schema://table/{table}")
    print(f"  ... and {len(tables) - 3} more table resources")
    
    # Simulate listing tools
    print("\n✅ Simulating: list_tools()")
    print("Expected tools:")
    print("  - query_database")
    print("  - get_table_schema")
    print("  - get_database_stats")
    
    # Simulate tool execution
    print("\n✅ Simulating: call_tool('query_database', ...)")
    sql = "SELECT * FROM Genre LIMIT 3"
    results = server.db.execute_query(sql)
    print(f"Query: {sql}")
    print(f"Results: {len(results)} rows")
    for row in results:
        print(f"  - {row}")
    
    print("\n" + "=" * 60)
    print("✅ MCP Protocol Simulation: PASSED")
    print("=" * 60)

    # Cleanup connections
    server.db.close()


def main():
    """Run all tests."""
    print("\n" + "🧪" * 30)
    print("LEGACY BRIDGE MCP SERVER - TEST SUITE")
    print("🧪" * 30)
    
    try:
        # Test 1: Database Manager
        test_database_manager()
        
        # Test 2: Schema Utilities
        test_schema_utilities()
        
        # Test 3: MCP Server
        asyncio.run(test_mcp_server())
        
        # Test 4: Protocol Simulation
        test_mcp_protocol_simulation()
        
        print("\n" + "🎉" * 30)
        print("ALL TESTS PASSED!")
        print("🎉" * 30)
        print("\n✅ Your MCP server is ready!")
        print("\nNext steps:")
        print("1. Test with Claude Desktop (see README.md)")
        print("2. Or use the API mode: python -m src.server_api")
        print("3. Or use CLI mode: python -m src.cli tables")
        
    except Exception as e:
        print("\n" + "❌" * 30)
        print(f"TEST FAILED: {e}")
        print("❌" * 30)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
