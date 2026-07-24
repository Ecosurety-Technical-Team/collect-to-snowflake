from pathlib import Path
from typing import TypedDict

type Sql = str


class CollectTable(TypedDict):
    mssql_table: str  # e.g. "dbo.ProductVerified"
    parquet_path: Path  # to persist fetched data locally
    custom_query: Sql
