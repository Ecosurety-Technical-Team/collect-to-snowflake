import logging
import textwrap

from snowflake.connector import SnowflakeConnection, connect

from src import casing
from src.common_types import CollectTable, Sql
from src.config import Config

logger = logging.getLogger(__name__)


def _clean_query(raw: Sql) -> Sql:
    return textwrap.dedent(raw).strip()


def _render_parquet_file_format(config: Config) -> str:
    return f"{config.snowflake_database}.{config.snowflake_schema}.PARQUET"


def _render_stage(config: Config) -> str:
    return f"{config.snowflake_database}.{config.snowflake_schema}.COLLECT_TO_SNOWFLAKE_CLI"


def _render_table(config: Config, collect_table: CollectTable) -> str:
    table = casing.pascal_case_to_upper_case(collect_table["mssql_table"])
    return f"{config.snowflake_database}.{config.snowflake_schema}.{table}"


def _render_staged_file_path(config: Config, collect_table: CollectTable) -> str:
    parquet_path = collect_table["parquet_path"]
    stage = _render_stage(config)
    stage_prefix = casing.pascal_case_to_upper_case(collect_table["mssql_table"])
    stage_path = f"{stage}/{stage_prefix}/{parquet_path.name}"
    return stage_path


def _create_file_format_if_missing(config: Config, conn: SnowflakeConnection) -> None:
    parquet_format = _render_parquet_file_format(config)
    logger.info(f"creating file format if missing: {parquet_format}")
    query = _clean_query(
        f"""
        CREATE FILE FORMAT IF NOT EXISTS {parquet_format}
            TYPE = PARQUET
            USE_LOGICAL_TYPE = TRUE
            USE_VECTORIZED_SCANNER = TRUE
            BINARY_AS_TEXT = FALSE
        ;
        """
    )
    with conn.cursor() as cursor:
        logger.debug("executing SQL query:\n%s", query)
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.debug("query result: %s", rows)


def _create_stage_if_missing(config: Config, conn: SnowflakeConnection) -> None:
    parquet_format = _render_parquet_file_format(config)
    stage = _render_stage(config)
    logger.info(f"creating stage if missing: {stage}")
    query = _clean_query(
        f"""
        CREATE STAGE IF NOT EXISTS {stage}
            FILE_FORMAT = {parquet_format}
            COMMENT = 'Parquet files with Collect data, downloaded using the `collect_to_snowflake` CLI'
        ;
        """
    )
    with conn.cursor() as cursor:
        logger.debug("executing SQL query:\n%s", query)
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.debug("query result: %s", rows)


def _upload_file_to_stage(
    config: Config, conn: SnowflakeConnection, collect_table: CollectTable
) -> None:
    parquet_path = collect_table["parquet_path"]
    stage_path = _render_staged_file_path(config=config, collect_table=collect_table)
    logger.info(f"uploading {parquet_path} to {stage_path}")

    # This query is idempotent by default
    query = f"PUT file://{parquet_path} @{stage_path}/{parquet_path.name};"

    with conn.cursor() as cursor:
        logger.debug("executing SQL query:\n%s", query)
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.debug("query result: %s", rows)


def _create_table_if_missing(
    config: Config, conn: SnowflakeConnection, collect_table: CollectTable
) -> None:
    parquet_format = _render_parquet_file_format(config)
    table = _render_table(config, collect_table)
    logger.info(f"creating table if missing: {table}")
    stage_path = _render_staged_file_path(config=config, collect_table=collect_table)
    query = _clean_query(
        f"""
        CREATE TABLE IF NOT EXISTS {table}
            USING TEMPLATE (
                SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                FROM TABLE(
                    INFER_SCHEMA(
                        LOCATION      => '@{stage_path}'
                        , FILE_FORMAT => '{parquet_format}'
                    )
                )
            )
            COMMENT = 'Table schema dynamically inferred from {stage_path}'
        ;
        """
    )
    with conn.cursor() as cursor:
        logger.debug("executing SQL query:\n%s", query)
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.debug("query result: %s", rows)


def _ingest_file_from_stage_into_table(
    config: Config, conn: SnowflakeConnection, collect_table: CollectTable
) -> None:
    parquet_format = _render_parquet_file_format(config)
    table = _render_table(config, collect_table)
    stage_path = _render_staged_file_path(config=config, collect_table=collect_table)
    logger.info(f"ingesting {stage_path} data into {table}")
    query = _clean_query(
        f"""
        COPY INTO {table}
        FROM '@{stage_path}'
            FILE_FORMAT = (FORMAT_NAME = '{parquet_format}')
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            FORCE = FALSE -- makes the query idempotent
        ;
        """
    )

    with conn.cursor() as cursor:
        logger.debug("executing SQL query:\n%s", query)
        cursor.execute(query)
        if logger.level == logging.DEBUG:
            rows = cursor.fetchall()
            logger.debug(f"{rows=}")


def upload_collect_table(
    config: Config, conn: SnowflakeConnection, table: CollectTable
) -> None:
    _upload_file_to_stage(config=config, conn=conn, collect_table=table)
    _create_table_if_missing(config=config, conn=conn, collect_table=table)
    _ingest_file_from_stage_into_table(config=config, conn=conn, collect_table=table)


def upload_collect_tables(config: Config, tables: list[CollectTable]) -> None:
    with connect(
        account=config.snowflake_account,
        user=config.snowflake_user,
        password=config.snowflake_token,
        role=config.snowflake_role,
    ) as conn:
        _create_file_format_if_missing(config=config, conn=conn)
        _create_stage_if_missing(config=config, conn=conn)
        for table in tables:
            upload_collect_table(config=config, conn=conn, table=table)
