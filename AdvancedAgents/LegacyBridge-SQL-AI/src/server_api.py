"""Standalone API-based SQL Assistant using Anthropic Claude.

This script provides a command-line interface that uses the Anthropic API
directly, without requiring Claude Desktop. It implements the same functionality
as the MCP server but as a self-contained application.

Usage:
    python src/server_api.py "Show me all artists"
    python src/server_api.py "What are the top 5 customers by purchases?"
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from .database import DatabaseManager
from .schema import create_llm_context

# Load environment variables from .env file
load_dotenv()


class SQLAssistantAPI:
    """Standalone SQL Assistant using Anthropic API."""
    
    def __init__(
        self,
        db_path: Path | str,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None
    ):
        """Initialize the SQL Assistant.
        
        Args:
            db_path: Path to the SQLite database
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use (or set ANTHROPIC_MODEL env var)
            max_tokens: Max tokens for responses (or set MAX_TOKENS env var)
        """
        self.db = DatabaseManager(db_path)
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required! Set ANTHROPIC_API_KEY environment "
                "variable or pass api_key parameter."
            )
        
        # Get model from parameter or environment (with default)
        self.model = model or os.environ.get(
            "ANTHROPIC_MODEL",
            "claude-3-5-sonnet-20241022"
        )
        
        # Get max_tokens from parameter or environment (with default)
        self.max_tokens = max_tokens or int(os.environ.get("MAX_TOKENS", "2048"))
        
        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history = []
        
        print("🔧 SQL Assistant initialized")
        print(f"📊 Database: {db_path}")
        print(f"🤖 Model: {self.model}")
        print(f"📝 Max tokens: {self.max_tokens}")
        print(f"🎯 Tables: {', '.join(self.db.get_tables())}")
        print()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt with database schema."""
        schema = self.db.get_full_schema()
        schema_context = create_llm_context(schema)
        
        return f"""You are a SQL expert assistant with access to a Chinook database.

{schema_context}

Your job is to:
1. Understand user questions about the database
2. Generate appropriate SQL queries (SELECT only)
3. Execute the queries using the query_database tool
4. Present results in a clear, user-friendly format

Important rules:
- Only generate SELECT queries (read-only)
- Always use proper SQL syntax for SQLite
- If a query fails, explain why and suggest corrections
- Present results in a clear, formatted way
- If asked about the database structure, reference the schema above
"""
    
    def _get_tools(self) -> list[dict[str, Any]]:
        """Get tool definitions for Claude."""
        return [
            {
                "name": "query_database",
                "description": (
                    "Execute a read-only SQL query against the Chinook database. "
                    "Only SELECT queries are allowed. Returns query results as JSON."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "The SQL SELECT query to execute"
                        }
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "get_table_schema",
                "description": (
                    "Get detailed schema information for a specific table. "
                    "Use this to understand table structure before querying."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to inspect"
                        }
                    },
                    "required": ["table_name"]
                }
            }
        ]
    
    def _execute_tool(self, tool_name: str, tool_input: dict) -> dict[str, Any]:
        """Execute a tool and return results.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool parameters
            
        Returns:
            Tool execution results
        """
        try:
            if tool_name == "query_database":
                sql = tool_input["sql"]
                print(f"🔍 Executing SQL: {sql}")
                
                results = self.db.execute_query(sql)
                
                return {
                    "success": True,
                    "rows": results,
                    "count": len(results),
                    "message": f"Query returned {len(results)} row(s)"
                }
            
            elif tool_name == "get_table_schema":
                table_name = tool_input["table_name"]
                print(f"📋 Getting schema for table: {table_name}")
                
                columns = self.db.get_table_schema(table_name)
                
                return {
                    "success": True,
                    "table": table_name,
                    "columns": columns
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
        
        except Exception as e:
            print(f"❌ Tool execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def query(self, user_message: str, max_turns: int = 10) -> str:
        """Process a user query using Claude API.
        
        Args:
            user_message: User's natural language question
            max_turns: Maximum conversation turns (prevents infinite loops)
            
        Returns:
            Claude's response
        """
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        print(f"💬 User: {user_message}\n")
        
        # Conversation loop (handles tool use)
        for turn in range(max_turns):
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self._get_system_prompt(),
                tools=self._get_tools(),
                messages=self.conversation_history
            )
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Add Claude's response to conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Execute all tools Claude requested
                tool_results = []
                
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        
                        # Execute the tool
                        result = self._execute_tool(tool_name, tool_input)
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": json.dumps(result)
                        })
                
                # Send tool results back to Claude
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            
            elif response.stop_reason == "end_turn":
                # Claude is done, extract final response
                final_response = ""
                for content_block in response.content:
                    if hasattr(content_block, "text"):
                        final_response += content_block.text
                
                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                return final_response
            
            else:
                # Unexpected stop reason
                return f"Unexpected stop reason: {response.stop_reason}"
        
        return "⚠️ Max conversation turns reached. Query may be too complex."
    
    def interactive_mode(self):
        """Run in interactive mode (chat loop)."""
        print("🤖 Interactive SQL Assistant")
        print("=" * 50)
        print("Ask questions about the Chinook database.")
        print("Type 'exit' or 'quit' to stop.")
        print("=" * 50)
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == "clear":
                    self.conversation_history = []
                    print("🔄 Conversation history cleared\n")
                    continue
                
                response = self.query(user_input)
                print(f"\n🤖 Assistant: {response}\n")
                print("-" * 50)
                print()
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def get_database_path() -> Path:
    """Get the path to the Chinook database."""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    db_path = project_root / "data" / "chinook.db"
    
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at: {db_path}\n"
            "Please download the Chinook database first (see README.md)"
        )
    
    return db_path


def main():
    """Main entry point for API-based SQL Assistant."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SQL Assistant using Anthropic Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (chat with the assistant)
  python -m src.server_api
  
  # Single query mode
  python -m src.server_api "Show me all artists"
  python -m src.server_api "What are the top 5 customers by total purchases?"
  
  # With explicit API key
  python -m src.server_api --api-key sk-ant-... "List all genres"

Environment Variables:
  ANTHROPIC_API_KEY    Your Anthropic API key (required)
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query (if omitted, starts interactive mode)"
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        help="Claude model to use (or set ANTHROPIC_MODEL env var). "
             "Options: claude-3-5-sonnet-20241022 (default), "
             "claude-3-5-haiku-20241022 (fast/cheap), "
             "claude-3-haiku-20240307 (cheapest)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum tokens for responses (or set MAX_TOKENS env var). Default: 2048"
    )
    
    args = parser.parse_args()
    
    try:
        db_path = get_database_path()
        assistant = SQLAssistantAPI(
            db_path,
            api_key=args.api_key,
            model=args.model,
            max_tokens=args.max_tokens
        )
        
        if args.query:
            # Single query mode
            response = assistant.query(args.query)
            print(f"\n🤖 Assistant: {response}\n")
        else:
            # Interactive mode
            assistant.interactive_mode()
    
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ {e}")
        print("\nGet your API key from: https://console.anthropic.com/")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
