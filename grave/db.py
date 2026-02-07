"""Database persistence layer for GRAVE.

Handles SQLite storage for scan history, repository data, and tags.
Uses XDG Base Directory specification for data storage.
"""

import os
import sqlite3
from datetime import UTC
from pathlib import Path


def get_data_dir() -> Path:
    """Return the XDG-compliant data directory for GRAVE.

    Uses $XDG_DATA_HOME/grave/ if set, otherwise ~/.local/share/grave/
    """
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        data_dir = Path(xdg_data_home) / "grave"
    else:
        data_dir = Path.home() / ".local" / "share" / "grave"

    return data_dir


def get_db_path() -> Path:
    """Return the path to the SQLite database file."""
    return get_data_dir() / "grave.db"


def init_db() -> sqlite3.Connection:
    """Initialize the database and return a connection.

    Creates the database file and all tables if they don't exist.
    Auto-creates the data directory if needed.
    Sets up schema_version tracking for future migrations.

    Returns:
        sqlite3.Connection: Database connection with row_factory set to Row.
    """
    db_path = get_db_path()

    # Auto-create data directory
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Create tables
    cursor = conn.cursor()

    # Schema version tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        )
    """)

    # Check if schema_version is empty and initialize if needed
    cursor.execute("SELECT COUNT(*) FROM schema_version")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO schema_version (version) VALUES (1)")

    # Scans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            preset_name TEXT,
            timestamp TEXT NOT NULL,
            result_count INTEGER NOT NULL
        )
    """)

    # Repositories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT UNIQUE NOT NULL,
            description TEXT,
            language TEXT,
            stargazers_count INTEGER,
            forks_count INTEGER,
            watchers_count INTEGER,
            open_issues_count INTEGER,
            created_at TEXT,
            pushed_at TEXT,
            updated_at TEXT,
            html_url TEXT,
            topics TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        )
    """)

    # Junction table linking scans to repos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_repos (
            scan_id INTEGER NOT NULL,
            repo_id INTEGER NOT NULL,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
            FOREIGN KEY (repo_id) REFERENCES repos(id) ON DELETE CASCADE,
            PRIMARY KEY (scan_id, repo_id)
        )
    """)

    # Tags table for user annotations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (repo_id) REFERENCES repos(id) ON DELETE CASCADE
        )
    """)

    # Create indexes for common queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_language
        ON repos(language)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_first_seen
        ON repos(first_seen)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_stargazers
        ON repos(stargazers_count)
    """)

    conn.commit()
    return conn


def save_scan(
    conn: sqlite3.Connection,
    query: str,
    preset_name: str | None,
    items: list[dict],
) -> int:
    """Save a scan and its results to the database.

    Inserts a scan record and upserts all repositories found.
    Deduplicates repos by full_name, preserving first_seen but updating last_seen.

    Args:
        conn: Database connection
        query: Search query string
        preset_name: Name of preset used (or None)
        items: List of repository dicts from search_repos()

    Returns:
        int: The scan_id of the inserted scan
    """
    import json
    from datetime import datetime

    cursor = conn.cursor()
    timestamp = datetime.now(UTC).isoformat()

    # Insert scan record
    cursor.execute(
        """
        INSERT INTO scans (query, preset_name, timestamp, result_count)
        VALUES (?, ?, ?, ?)
        """,
        (query, preset_name, timestamp, len(items)),
    )
    scan_id = cursor.lastrowid

    # Upsert each repo
    for item in items:
        # Store topics as JSON
        topics_json = json.dumps(item.get("topics", []))

        # Check if repo exists to preserve first_seen
        cursor.execute(
            "SELECT id, first_seen FROM repos WHERE full_name = ?",
            (item["full_name"],),
        )
        existing = cursor.fetchone()

        if existing:
            # Update existing repo
            repo_id = existing["id"]

            cursor.execute(
                """
                UPDATE repos SET
                    description = ?,
                    language = ?,
                    stargazers_count = ?,
                    forks_count = ?,
                    watchers_count = ?,
                    open_issues_count = ?,
                    created_at = ?,
                    pushed_at = ?,
                    updated_at = ?,
                    html_url = ?,
                    topics = ?,
                    last_seen = ?
                WHERE full_name = ?
                """,
                (
                    item.get("description"),
                    item.get("language"),
                    item.get("stargazers_count"),
                    item.get("forks_count"),
                    item.get("watchers_count"),
                    item.get("open_issues_count"),
                    item.get("created_at"),
                    item.get("pushed_at"),
                    item.get("updated_at"),
                    item.get("html_url"),
                    topics_json,
                    timestamp,
                    item["full_name"],
                ),
            )
        else:
            # Insert new repo
            cursor.execute(
                """
                INSERT INTO repos (
                    full_name, description, language, stargazers_count,
                    forks_count, watchers_count, open_issues_count,
                    created_at, pushed_at, updated_at, html_url, topics,
                    first_seen, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["full_name"],
                    item.get("description"),
                    item.get("language"),
                    item.get("stargazers_count"),
                    item.get("forks_count"),
                    item.get("watchers_count"),
                    item.get("open_issues_count"),
                    item.get("created_at"),
                    item.get("pushed_at"),
                    item.get("updated_at"),
                    item.get("html_url"),
                    topics_json,
                    timestamp,
                    timestamp,
                ),
            )
            repo_id = cursor.lastrowid

        # Link scan to repo
        cursor.execute(
            """
            INSERT OR IGNORE INTO scan_repos (scan_id, repo_id)
            VALUES (?, ?)
            """,
            (scan_id, repo_id),
        )

    conn.commit()
    return scan_id


def save_repo(conn: sqlite3.Connection, repo_data: dict) -> int:
    """Save or update a single repository in the database.

    Used for saving enriched data from get_repo() API calls.
    Normalizes field names from GitHub API format and upserts the record.

    Args:
        conn: Database connection
        repo_data: Repository dict from get_repo() (raw GitHub API format)

    Returns:
        int: The repo_id
    """
    import json
    from datetime import datetime

    cursor = conn.cursor()
    timestamp = datetime.now(UTC).isoformat()

    # Normalize field names (get_repo returns camelCase from GitHub API)
    full_name = repo_data["full_name"]
    topics_json = json.dumps(repo_data.get("topics", []))

    # Check if repo exists to preserve first_seen
    cursor.execute(
        "SELECT id, first_seen FROM repos WHERE full_name = ?",
        (full_name,),
    )
    existing = cursor.fetchone()

    if existing:
        # Update existing repo
        repo_id = existing["id"]

        cursor.execute(
            """
            UPDATE repos SET
                description = ?,
                language = ?,
                stargazers_count = ?,
                forks_count = ?,
                watchers_count = ?,
                open_issues_count = ?,
                created_at = ?,
                pushed_at = ?,
                updated_at = ?,
                html_url = ?,
                topics = ?,
                last_seen = ?
            WHERE full_name = ?
            """,
            (
                repo_data.get("description"),
                repo_data.get("language"),
                repo_data.get("stargazers_count"),
                repo_data.get("forks_count"),
                repo_data.get("watchers_count"),
                repo_data.get("open_issues_count"),
                repo_data.get("created_at"),
                repo_data.get("pushed_at"),
                repo_data.get("updated_at"),
                repo_data.get("html_url"),
                topics_json,
                timestamp,
                full_name,
            ),
        )
    else:
        # Insert new repo
        cursor.execute(
            """
            INSERT INTO repos (
                full_name, description, language, stargazers_count,
                forks_count, watchers_count, open_issues_count,
                created_at, pushed_at, updated_at, html_url, topics,
                first_seen, last_seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                repo_data.get("description"),
                repo_data.get("language"),
                repo_data.get("stargazers_count"),
                repo_data.get("forks_count"),
                repo_data.get("watchers_count"),
                repo_data.get("open_issues_count"),
                repo_data.get("created_at"),
                repo_data.get("pushed_at"),
                repo_data.get("updated_at"),
                repo_data.get("html_url"),
                topics_json,
                timestamp,
                timestamp,
            ),
        )
        repo_id = cursor.lastrowid

    conn.commit()
    return repo_id


def list_repos(
    conn: sqlite3.Connection,
    language: str | None = None,
    stars: str | None = None,
    preset: str | None = None,
    since: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List repositories from the database with optional filters.

    Args:
        conn: Database connection
        language: Filter by programming language
        stars: Filter by star count (e.g., ">100", "<50", "100..200")
        preset: Filter by preset name (from scan)
        since: Filter by first_seen date (ISO format)
        limit: Maximum number of results (default 50)

    Returns:
        list[dict]: List of repository dicts with normalized fields
    """
    import json

    cursor = conn.cursor()

    # Build query with filters
    query_parts = ["SELECT DISTINCT repos.* FROM repos"]
    where_clauses = []
    params = []

    # Join with scans if preset filter is specified
    if preset:
        query_parts.append(
            """
            INNER JOIN scan_repos ON repos.id = scan_repos.repo_id
            INNER JOIN scans ON scan_repos.scan_id = scans.id
            """
        )
        where_clauses.append("scans.preset_name = ?")
        params.append(preset)

    # Language filter
    if language:
        where_clauses.append("repos.language = ?")
        params.append(language)

    # Stars filter
    if stars:
        if stars.startswith(">"):
            where_clauses.append("repos.stargazers_count > ?")
            params.append(int(stars[1:]))
        elif stars.startswith("<"):
            where_clauses.append("repos.stargazers_count < ?")
            params.append(int(stars[1:]))
        elif ".." in stars:
            parts = stars.split("..")
            where_clauses.append(
                "repos.stargazers_count >= ? AND repos.stargazers_count <= ?"
            )
            params.extend([int(parts[0]), int(parts[1])])
        else:
            where_clauses.append("repos.stargazers_count = ?")
            params.append(int(stars))

    # Since filter
    if since:
        where_clauses.append("repos.first_seen >= ?")
        params.append(since)

    # Combine query
    if where_clauses:
        query_parts.append("WHERE " + " AND ".join(where_clauses))

    query_parts.append("ORDER BY repos.first_seen DESC")
    query_parts.append("LIMIT ?")
    params.append(limit)

    full_query = " ".join(query_parts)

    # Execute and fetch
    cursor.execute(full_query, params)
    rows = cursor.fetchall()

    # Convert to dicts with parsed topics
    results = []
    for row in rows:
        repo = dict(row)
        # Parse topics from JSON
        repo["topics"] = json.loads(repo.get("topics", "[]"))
        results.append(repo)

    return results


def get_db_stats(conn: sqlite3.Connection) -> dict:
    """Get database statistics.

    Args:
        conn: Database connection

    Returns:
        dict: Statistics including counts, sizes, dates, and top languages
    """
    cursor = conn.cursor()

    # Total repos
    cursor.execute("SELECT COUNT(*) FROM repos")
    total_repos = cursor.fetchone()[0]

    # Total scans
    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]

    # DB file size
    db_path = get_db_path()
    db_size = db_path.stat().st_size if db_path.exists() else 0

    # Oldest repo first_seen
    cursor.execute("SELECT MIN(first_seen) FROM repos")
    oldest_first_seen = cursor.fetchone()[0]

    # Newest repo first_seen
    cursor.execute("SELECT MAX(first_seen) FROM repos")
    newest_first_seen = cursor.fetchone()[0]

    # Top 5 languages
    cursor.execute(
        """
        SELECT language, COUNT(*) as count
        FROM repos
        WHERE language IS NOT NULL
        GROUP BY language
        ORDER BY count DESC
        LIMIT 5
        """
    )
    top_languages = [
        {"language": row["language"], "count": row["count"]}
        for row in cursor.fetchall()
    ]

    return {
        "total_repos": total_repos,
        "total_scans": total_scans,
        "db_size": db_size,
        "oldest_first_seen": oldest_first_seen,
        "newest_first_seen": newest_first_seen,
        "top_languages": top_languages,
    }


def clear_all(conn: sqlite3.Connection) -> None:
    """Clear all data from the database.

    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tags")
    cursor.execute("DELETE FROM scan_repos")
    cursor.execute("DELETE FROM scans")
    cursor.execute("DELETE FROM repos")
    conn.commit()


def clear_scans(conn: sqlite3.Connection) -> None:
    """Clear only scan history, keeping repos.

    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scan_repos")
    cursor.execute("DELETE FROM scans")
    conn.commit()


def vacuum_db(conn: sqlite3.Connection) -> None:
    """Run SQLite VACUUM to compact the database.

    Args:
        conn: Database connection
    """
    conn.execute("VACUUM")
    conn.commit()
