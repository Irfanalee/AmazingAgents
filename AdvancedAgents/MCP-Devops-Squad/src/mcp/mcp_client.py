import asyncio
from contextlib import AsyncExitStack
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.utils.logger import setup_logger

class MCPClient:
    """A client to interact with multiple MCP servers via stdio."""
    def __init__(self):
        self.logger = setup_logger("MCP-Client")
        self._exit_stack = AsyncExitStack()
        self._sessions: Dict[str, ClientSession] = {}

    async def connect_to_server(self, name: str, command: str, args: List[str]):
        """Connect to an MCP server using stdio transport and verify connection."""
        self.logger.info("connecting_to_server", server=name, command=command, args=args)
        server_params = StdioServerParameters(command=command, args=args, env=None)
        
        try:
            read, write = await self._exit_stack.enter_async_context(stdio_client(server_params))
            session = await self._exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            
            # Verification step: list tools to ensure the server is responsive
            tools = await session.list_tools()
            self._sessions[name] = session
            self.logger.info("connected_to_server", server=name, tools_found=len(tools.tools))
        except Exception as e:
            self.logger.error("connection_failed", server=name, error=str(e))
            raise

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific MCP server."""
        if server_name not in self._sessions:
            raise ValueError(f"No session found for server: {server_name}")
        
        session = self._sessions[server_name]
        self.logger.info("calling_tool", server=server_name, tool=tool_name, args=arguments)
        
        try:
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            self.logger.error("tool_call_failed", server=server_name, tool=tool_name, error=str(e))
            raise

    async def list_tools(self, server_name: str) -> List[Any]:
        """List available tools on a specific MCP server."""
        if server_name not in self._sessions:
            raise ValueError(f"No session found for server: {server_name}")
        
        session = self._sessions[server_name]
        result = await session.list_tools()
        return result.tools

    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        await self._exit_stack.aclose()
        self._sessions.clear()
        self.logger.info("disconnected_all_servers")

    # Synchronous wrapper for convenience in existing agents
    def sync_call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Synchronous wrapper for call_tool."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # In a running loop (like some test runners), we can't use run_until_complete
            # This is a complex case for sync-over-async
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(self.call_tool(server_name, tool_name, arguments))
        else:
            return loop.run_until_complete(self.call_tool(server_name, tool_name, arguments))

    def sync_connect(self, name: str, command: str, args: List[str]):
        """Synchronous wrapper for connect_to_server."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(self.connect_to_server(name, command, args))
        else:
            return loop.run_until_complete(self.connect_to_server(name, command, args))
