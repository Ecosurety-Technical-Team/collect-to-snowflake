from pathlib import Path

import pyarrow.parquet as pq

type ColumnName = str


def read_column_names(path: Path) -> list[ColumnName]:
    table = pq.read_table(path)
    return table.column_names


def update_column_names(path: Path, map: dict[str, str]) -> None:
    table = pq.read_table(path)
    updated_column_names = [map[column] for column in table.column_names]
    table = table.rename_columns(updated_column_names)
    pq.write_table(table, path)
