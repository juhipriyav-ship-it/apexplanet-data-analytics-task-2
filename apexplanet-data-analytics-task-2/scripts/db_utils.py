"""
db_utils.py
===========
Reusable MySQL database utilities for ApexPlanet Data Analytics - Task 2
(SQL for Data Extraction).

This module is the single place where every script and notebook in this
project talks to the database.  It handles:

    * reading connection settings from ``.env``           -> get_settings()
    * building cached SQLAlchemy engines                  -> get_engine()
    * running SELECT queries as a pandas DataFrame        -> run_query()
    * running DDL / DML statements                        -> execute()
    * bulk-loading the cleaned CSV into a table           -> load_csv_to_mysql()
    * creating the database and table from the .sql files -> build_database()
    * listing tables and views                            -> list_tables()

Command line usage
------------------
    python scripts/db_utils.py --load
        Create the database, create the table and load the cleaned CSV.

    python scripts/db_utils.py --query "SELECT COUNT(*) FROM superstore"
        Run an ad-hoc query and print the result.

    python scripts/db_utils.py --tables
        List the tables and views in the project database.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# --------------------------------------------------------------------------- #
# Paths and constants
# --------------------------------------------------------------------------- #

#: Project root (the folder that contains this ``scripts`` directory).
ROOT = Path(__file__).resolve().parents[1]

#: Location of the credentials file.  ``.env`` is gitignored - never commit it.
ENV_FILE = ROOT / ".env"

#: The cleaned dataset produced during Task 1.
CLEANED_CSV = ROOT.parent / "data" / "superstore_cleaned.csv"

#: Name of the table that holds the Superstore rows.
TABLE_NAME = "superstore"

#: SQL files, applied in this order when building the database.
SQL_FILES = (
    ROOT / "sql" / "01_schema.sql",
    ROOT / "sql" / "05_views.sql",
)

#: Module level cache so a script does not open a new pool for every query.
_ENGINES: dict[str, Engine] = {}


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #


def load_env(path: Path | str = ENV_FILE) -> dict[str, str]:
    """Parse a simple ``KEY=VALUE`` .env file into a dictionary.

    Values may be wrapped in single or double quotes.  Blank lines and lines
    starting with ``#`` are ignored.  If the file is missing, an empty
    dictionary is returned so callers can fall back to real environment
    variables instead.
    """
    path = Path(path)
    env: dict[str, str] = {}

    if not path.exists():
        return env

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        env[key.strip()] = value

    return env


def get_settings(database: str | None = None) -> dict[str, Any]:
    """Return MySQL connection settings.

    Values are taken from ``.env`` first and from real environment variables
    second, so the same code works locally and in CI.

    Parameters
    ----------
    database:
        Override the database name from ``.env``.  Pass ``""`` to connect to
        the server without selecting a database.
    """
    env = load_env()

    def setting(key: str, default: str) -> str:
        return env.get(key) or os.environ.get(key) or default

    db = setting("MYSQL_DATABASE", "apexplanet") if database is None else database

    return {
        "host": setting("MYSQL_HOST", "127.0.0.1"),
        "port": int(setting("MYSQL_PORT", "3306")),
        "user": setting("MYSQL_USER", "root"),
        "password": setting("MYSQL_PASSWORD", ""),
        "database": db,
    }


def get_engine(database: str | None = None) -> Engine:
    """Return a cached SQLAlchemy engine.

    Pass ``database=""`` to get an engine for the server itself, which is what
    ``CREATE DATABASE`` needs.
    """
    settings = get_settings(database)
    db = settings["database"]
    cache_key = db or "__server__"

    if cache_key not in _ENGINES:
        url = (
            f"mysql+mysqlconnector://{settings['user']}:{settings['password']}"
            f"@{settings['host']}:{settings['port']}/{db}"
        )
        _ENGINES[cache_key] = create_engine(url, pool_pre_ping=True, future=True)

    return _ENGINES[cache_key]


# --------------------------------------------------------------------------- #
# Running queries
# --------------------------------------------------------------------------- #


def run_query(sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
    """Run a SELECT statement and return the result as a DataFrame."""
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def execute(sql: str, params: dict[str, Any] | None = None) -> int:
    """Run a single DDL/DML statement and return the affected row count.

    Statements are executed inside a transaction that is committed on success
    and rolled back on failure.
    """
    statements = [s.strip() for s in _split_statements(sql) if s.strip()]
    affected = 0

    with get_engine().begin() as conn:
        for statement in statements:
            result = conn.execute(text(statement), params or {})
            if result.rowcount and result.rowcount > 0:
                affected += result.rowcount

    return affected


def _split_statements(sql: str) -> list[str]:
    """Split a .sql file into individual statements on semicolons.

    Good enough for this project: it ignores semicolons that appear inside
    line comments (``--`` or ``#``) and inside quoted strings.  It is
    deliberately not a full SQL parser - there is no support for block
    comments or for ``;`` inside stored procedure bodies.
    """
    statements: list[str] = []
    buffer: list[str] = []
    quote: str | None = None
    index = 0
    length = len(sql)

    while index < length:
        char = sql[index]
        pair = sql[index : index + 2]

        if quote:
            buffer.append(char)
            if char == quote:
                quote = None
            index += 1
            continue

        # Line comments run until the end of the line.
        if pair == "--" or char == "#":
            end = sql.find("\n", index)
            if end == -1:
                break
            index = end + 1
            continue

        if char in ("'", '"', "`"):
            quote = char
            buffer.append(char)
            index += 1
            continue

        if char == ";":
            statements.append("".join(buffer))
            buffer = []
            index += 1
            continue

        buffer.append(char)
        index += 1

    statements.append("".join(buffer))
    return statements


# --------------------------------------------------------------------------- #
# Loading data
# --------------------------------------------------------------------------- #


def read_cleaned_data(csv_path: Path | str = CLEANED_CSV) -> pd.DataFrame:
    """Read the Task 1 cleaned dataset from disk."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at {csv_path}. "
            "Run Task 1 first or pass an explicit csv_path."
        )
    return pd.read_csv(csv_path)


def build_database(verbose: bool = True) -> None:
    """Create the database and its schema by running the project .sql files."""
    settings = get_settings()
    db_name = settings["database"]

    # 1. Create the database itself (needs a server-level connection).
    with get_engine(database="").begin() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        if verbose:
            print(f"[ok] database ready: {db_name}")

    # 2. Apply the schema / view files in order.
    for sql_file in SQL_FILES:
        if not sql_file.exists():
            if verbose:
                print(f"[skip] {sql_file.name} not found")
            continue
        execute(sql_file.read_text(encoding="utf-8"))
        if verbose:
            print(f"[ok] applied {sql_file.name}")


def load_csv_to_mysql(
    csv_path: Path | str = CLEANED_CSV,
    table: str = TABLE_NAME,
    if_exists: str = "append",
    truncate: bool = True,
    verbose: bool = True,
) -> int:
    """Load the cleaned CSV into MySQL and return the number of rows written.

    ``if_exists='append'`` (the default) is used together with the ``CREATE
    TABLE`` statement from ``01_schema.sql`` so the column types are explicit
    rather than guessed by pandas.

    When ``truncate`` is true (the default) the table is emptied first, which
    makes re-running the load idempotent instead of doubling the row count.
    """
    df = read_cleaned_data(csv_path)
    df.columns = [_to_snake_case(c) for c in df.columns]

    # Dates are stored as text in the CSV; keep MySQL's YYYY-MM-DD format.
    for column in ("order_date", "ship_date"):
        if column in df.columns:
            df[column] = pd.to_datetime(df[column]).dt.strftime("%Y-%m-%d")

    if truncate and if_exists == "append" and table_exists(table):
        execute(f"TRUNCATE TABLE `{table}`")
        if verbose:
            print(f"[ok] cleared existing rows from {table}")

    df.to_sql(
        table,
        get_engine(),
        if_exists=if_exists,
        index=False,
        chunksize=500,
    )

    if verbose:
        print(f"[ok] loaded {len(df):,} rows into {table}")

    return len(df)


def _to_snake_case(name: str) -> str:
    """``'Sub-Category'`` -> ``'sub_category'``, ``'Row ID'`` -> ``'row_id'``."""
    cleaned = name.strip().replace("-", "_").replace(" ", "_")
    return cleaned.lower()


# --------------------------------------------------------------------------- #
# Introspection helpers
# --------------------------------------------------------------------------- #


def list_tables(verbose: bool = True) -> list[str]:
    """List the tables in the project database."""
    df = run_query("SHOW TABLES")
    tables = df.iloc[:, 0].tolist() if not df.empty else []
    if verbose:
        print(f"Tables in {get_settings()['database']}:")
        for table in tables:
            print(f"  - {table} (rows: {row_count(table):,})")
    return tables


def row_count(table: str = TABLE_NAME) -> int:
    """Return the number of rows in a table."""
    with get_engine().connect() as conn:
        return int(conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar_one())


def table_exists(table: str = TABLE_NAME) -> bool:
    """Return True when ``table`` exists in the project database."""
    df = run_query(
        """
        SELECT COUNT(*) AS found
        FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = :table
        """,
        {"table": table},
    )
    return int(df.iloc[0, 0]) > 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main() -> None:
    parser = argparse.ArgumentParser(description="MySQL utilities for Task 2")
    parser.add_argument(
        "--load",
        action="store_true",
        help="create the database, apply the schema and load the cleaned CSV",
    )
    parser.add_argument("--query", metavar="SQL", help="run an ad-hoc query and print it")
    parser.add_argument("--tables", action="store_true", help="list tables and row counts")
    args = parser.parse_args()

    if args.load:
        build_database()
        load_csv_to_mysql()
        list_tables()

    if args.query:
        with pd.option_context("display.max_columns", None, "display.width", 200):
            print(run_query(args.query))

    if args.tables:
        list_tables()

    if not any((args.load, args.query, args.tables)):
        parser.print_help()


if __name__ == "__main__":
    main()
