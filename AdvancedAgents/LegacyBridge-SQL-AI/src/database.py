"""Database connection and query execution module.

This module handles all interactions with the SQLite database,
including connection management, query execution, and schema inspection.
"""

import sqlite3
from pathlib import Path
from typing import Any
from contextlib import contextmanager
from queue import Queue, Empty
import threading


class ConnectionPool:
    """Thread-safe connection pool for SQLite database.

    This pool manages a fixed number of database connections that can be
    reused across multiple queries, improving performance by avoiding
    the overhead of creating new connections for each operation.
    """

    def __init__(self, db_path: Path, pool_size: int = 5, timeout: float = 30.0):
        """Initialize the connection pool.

        Args:
            db_path: Path to the SQLite database file
            pool_size: Maximum number of connections in the pool
            timeout: Maximum time to wait for an available connection (seconds)
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0

        # Pre-create connections up to pool_size
        for _ in range(pool_size):
            self._pool.put(self._create_connection())

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimal settings.

        Returns:
            Configured SQLite connection
        """
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow connection sharing across threads
            timeout=self.timeout
        )
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent read performance
        conn.execute("PRAGMA journal_mode=WAL")
        # Set busy timeout for handling concurrent access
        conn.execute(f"PRAGMA busy_timeout={int(self.timeout * 1000)}")
        self._created_connections += 1
        return conn

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool (context manager).

        Yields:
            Database connection from the pool

        Raises:
            TimeoutError: If no connection becomes available within timeout period
        """
        conn = None
        try:
            conn = self._pool.get(timeout=self.timeout)
            yield conn
        except Empty:
            raise TimeoutError(
                f"Could not acquire database connection within {self.timeout} seconds. "
                f"Pool size: {self.pool_size}, Created: {self._created_connections}"
            )
        finally:
            if conn is not None:
                # Return connection to pool
                self._pool.put(conn)

    def close_all(self):
        """Close all connections in the pool.

        Should be called when shutting down the application.
        """
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except Empty:
                    break

    def __del__(self):
        """Cleanup connections when pool is destroyed."""
        self.close_all()


class DatabaseManager:
    """Manages database connections and operations with connection pooling."""

    def __init__(self, db_path: Path | str, pool_size: int = 5, timeout: float = 30.0):
        """Initialize the database manager with connection pooling.

        Args:
            db_path: Path to the SQLite database file
            pool_size: Maximum number of connections in the pool (default: 5)
            timeout: Maximum time to wait for connection (seconds, default: 30)

        Raises:
            FileNotFoundError: If database file doesn't exist
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at: {self.db_path}")

        # Initialize connection pool
        self.pool = ConnectionPool(self.db_path, pool_size, timeout)
    
    def execute_query(self, sql: str) -> list[dict[str, Any]]:
        """Execute a SQL query and return results using connection pool.

        Args:
            sql: SQL query to execute (must be SELECT statement)

        Returns:
            List of rows as dictionaries

        Raises:
            ValueError: If query is not a SELECT statement
            sqlite3.Error: If query execution fails
        """
        # Validate read-only (only SELECT statements allowed)
        sql_stripped = sql.strip().upper()
        if not sql_stripped.startswith("SELECT"):
            raise ValueError(
                "Only SELECT queries are allowed (read-only mode). "
                f"Query started with: {sql_stripped.split()[0]}"
            )

        # Check for dangerous keywords that might bypass SELECT restriction
        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]
        for keyword in dangerous_keywords:
            if keyword in sql_stripped:
                raise ValueError(
                    f"Query contains forbidden keyword: {keyword}. "
                    "Only pure SELECT queries are allowed."
                )

        # Use connection from pool
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_tables(self) -> list[str]:
        """Get list of all tables in the database.
        
        Returns:
            List of table names
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.execute_query(sql)
        return [row["name"] for row in results]
    
    def get_table_schema(self, table_name: str) -> list[dict[str, Any]]:
        """Get schema information for a specific table using connection pool.

        Args:
            table_name: Name of the table

        Returns:
            List of column definitions with metadata

        Raises:
            ValueError: If table doesn't exist
        """
        # Validate table exists
        tables = self.get_tables()
        if table_name not in tables:
            raise ValueError(
                f"Table '{table_name}' not found. "
                f"Available tables: {', '.join(tables)}"
            )

        sql = f"PRAGMA table_info({table_name})"

        # Use connection from pool
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_full_schema(self) -> dict[str, list[dict[str, Any]]]:
        """Get schema for all tables in the database.
        
        Returns:
            Dictionary mapping table names to their column definitions
        """
        schema = {}
        for table in self.get_tables():
            schema[table] = self.get_table_schema(table)
        return schema
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        sql = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(sql)
        return result[0]["count"]
    
    def get_database_stats(self) -> dict[str, Any]:
        """Get statistics about the database.

        Returns:
            Dictionary with database statistics
        """
        tables = self.get_tables()
        stats = {
            "database_path": str(self.db_path),
            "total_tables": len(tables),
            "tables": {}
        }

        for table in tables:
            stats["tables"][table] = {
                "columns": len(self.get_table_schema(table)),
                "rows": self.get_table_row_count(table)
            }

        return stats

    def close(self):
        """Close all connections in the pool.

        Should be called when shutting down the application to properly
        clean up database connections.
        """
        self.pool.close_all()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup connections."""
        self.close()
        return False
