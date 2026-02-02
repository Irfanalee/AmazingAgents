"""Test script to verify connection pooling performance improvements.

This script compares performance with and without connection pooling
by running concurrent database queries.
"""

import time
import concurrent.futures
from pathlib import Path
from src.database import DatabaseManager


def run_query(db_manager: DatabaseManager, query_num: int) -> float:
    """Execute a test query and return execution time."""
    start = time.time()
    result = db_manager.execute_query("SELECT * FROM Track LIMIT 10")
    duration = time.time() - start
    print(f"Query {query_num}: {len(result)} rows in {duration:.4f}s")
    return duration


def test_concurrent_queries(db_path: Path, num_queries: int = 20, pool_size: int = 5):
    """Test concurrent query performance with connection pooling."""
    print(f"\nTesting with {num_queries} concurrent queries (pool_size={pool_size})...")

    db_manager = DatabaseManager(db_path, pool_size=pool_size)

    start_time = time.time()

    # Run queries concurrently using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(run_query, db_manager, i)
            for i in range(num_queries)
        ]

        # Wait for all queries to complete
        durations = [f.result() for f in concurrent.futures.as_completed(futures)]

    total_time = time.time() - start_time
    avg_time = sum(durations) / len(durations)

    print(f"\nResults:")
    print(f"  Total time: {total_time:.4f}s")
    print(f"  Average query time: {avg_time:.4f}s")
    print(f"  Queries per second: {num_queries / total_time:.2f}")

    db_manager.close()

    return total_time, avg_time


def main():
    """Run connection pool tests."""
    # Get database path (tests folder is one level below project root)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    db_path = project_root / "data" / "chinook.db"

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    print("=" * 60)
    print("Connection Pool Performance Test")
    print("=" * 60)

    # Test with different pool sizes
    for pool_size in [1, 3, 5, 10]:
        test_concurrent_queries(db_path, num_queries=20, pool_size=pool_size)
        time.sleep(1)  # Brief pause between tests

    print("\n" + "=" * 60)
    print("Connection pooling is now enabled!")
    print("Benefits:")
    print("  - Reuses connections instead of creating new ones")
    print("  - Better performance under concurrent load")
    print("  - WAL mode enabled for improved read concurrency")
    print("  - Thread-safe connection management")
    print("=" * 60)


if __name__ == "__main__":
    main()
