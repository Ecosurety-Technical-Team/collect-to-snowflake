from __future__ import annotations

import logging
from pathlib import Path
from typing import Self

import duckdb

from src import paths
from src.common_types import Sql
from src.config import Config

logger = logging.getLogger(__name__)

SQL_DIR = paths.REPO_DIR / "sql"


def read_sql(path: Path) -> Sql:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text().strip()


class DuckDb:
    def __init__(self, config: Config):
        self.con = duckdb.connect()
        self.con.execute("INSTALL mssql FROM community; LOAD mssql;")
        logger.info("duckdb: MSSQL: installed and loaded")
        self.con.execute("INSTALL azure; LOAD azure;")
        logger.info("duckdb: Azure: installed and loaded")

        self.con.execute(
            "CREATE SECRET azure_interactive (TYPE azure, PROVIDER credential_chain, CHAIN 'cli')"
        )
        logger.info("duckdb: Azure: auth secret created")
        conn_str = (
            f"server={config.sql_server};database={config.sql_database};encrypt=yes;"
        )
        self.con.execute(
            f"ATTACH '{conn_str}'"
            " AS mssql (TYPE mssql, AZURE_SECRET 'azure_interactive')"
        )
        logger.info("duckdb: attached")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def execute(self, query: Sql) -> None:
        logger.info(f"executing query:\n{query}")
        self.con.execute(query)

    def execute_query_file(self, path: Path, output: Path) -> None:
        query = read_sql(path=path).replace(
            "__output_path__", str(output.expanduser().resolve())
        )
        logger.info(f"executing query:\n{query}")
        self.con.execute(query)

    def close(self) -> None:
        self.con.execute("DETACH mssql")
        self.con.close()
        logger.info("duck: connection closed")
