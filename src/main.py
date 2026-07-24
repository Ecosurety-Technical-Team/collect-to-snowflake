import argparse
import datetime
import logging
import textwrap

from snowflake.connector import connect as connect_to_snowflake

from src import checks, db, paths, snowflake
from src.common_types import CollectTable
from src.config import Config

logger = logging.getLogger(__name__)


today = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
COLLECT_TABLES: list[CollectTable] = [
    {
        "mssql_table": "dbo.ActiveUserSessions",
        "parquet_path": paths.REPO_DIR / f"dbo-active-user-sessions-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Approval",
        "parquet_path": paths.REPO_DIR / f"dbo-approval-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Assignment",
        "parquet_path": paths.REPO_DIR / f"dbo-assignment-{today}.parquet",
    },
    # {  # too big, and barely useful
    #     "mssql_table": "dbo.AssignmentAudit",
    #     "parquet_path": paths.REPO_DIR / f"dbo-assignment-audit-{today}.parquet",
    # },
    {
        "mssql_table": "dbo.AssignmentRequest",
        "parquet_path": paths.REPO_DIR / f"dbo-assignment-request-{today}.parquet",
    },
    {
        "mssql_table": "dbo.AssignmentStage",
        "parquet_path": paths.REPO_DIR / f"dbo-assignment-stage-{today}.parquet",
    },
    {
        "mssql_table": "dbo.AssignmentStatus",
        "parquet_path": paths.REPO_DIR / f"dbo-assignment-status-{today}.parquet",
    },
    {
        "mssql_table": "dbo.CheckTemplate",
        "parquet_path": paths.REPO_DIR / f"dbo-check-template-{today}.parquet",
    },
    {
        "mssql_table": "dbo.CheckType",
        "parquet_path": paths.REPO_DIR / f"dbo-check_type-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Collection",
        "parquet_path": paths.REPO_DIR / f"dbo-collection-{today}.parquet",
    },
    {
        "mssql_table": "dbo.CollectionCheck",
        "parquet_path": paths.REPO_DIR / f"dbo-collection_check-{today}.parquet",
    },
    {
        "mssql_table": "dbo.CollectUser",
        "parquet_path": paths.REPO_DIR / f"dbo-collect-user-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Company",
        "parquet_path": paths.REPO_DIR / f"dbo-company-{today}.parquet",
    },
    # {  # too big, and barely useful
    #     "mssql_table": "dbo.CompanyAudit",
    #     "parquet_path": paths.REPO_DIR / f"dbo-company-audit-{today}.parquet",
    # },
    {
        "mssql_table": "dbo.Component",
        "parquet_path": paths.REPO_DIR / f"dbo-component-{today}.parquet",
    },
    {
        "mssql_table": "dbo.ComponentApproval",
        "parquet_path": paths.REPO_DIR / f"dbo-component-approval-{today}.parquet",
    },
    # {  # too big, and barely useful
    #     "mssql_table": "dbo.ComponentAudit",
    #     "parquet_path": paths.REPO_DIR / f"dbo-component-audit-{today}.parquet",
    # },
    {
        "mssql_table": "dbo.ComponentEPR",
        "parquet_path": paths.REPO_DIR / f"dbo-component-epr-{today}.parquet",
        "custom_query": textwrap.dedent("""
            COPY (
              SELECT
                -- drop `RowVersion`, because MS SQL's explicitly forbids casting
                -- its `timestamp/rowversion` type (which is a binary) into
                -- anything useful
                * EXCLUDE (RowVersion)
                , current_timestamp AS EXPORTED_AT -- in UTC
              FROM mssql.{__MSSQL_TABLE__}
            ) TO '{__PARQUET_PATH__}' (FORMAT parquet)
            """).strip(),
    },
    {
        "mssql_table": "dbo.ComponentPackaging",
        "parquet_path": paths.REPO_DIR / f"dbo-component-packaging-{today}.parquet",
        "custom_query": textwrap.dedent("""
            COPY (
              SELECT
                -- drop `RowVersion`, because MS SQL's explicitly forbids casting
                -- its `timestamp/rowversion` type (which is a binary) into
                -- anything useful
                * EXCLUDE (RowVersion)
                , current_timestamp AS EXPORTED_AT -- in UTC
              FROM mssql.{__MSSQL_TABLE__}
            ) TO '{__PARQUET_PATH__}' (FORMAT parquet)
            """).strip(),
    },
    {
        "mssql_table": "dbo.ComponentStage",
        "parquet_path": paths.REPO_DIR / f"dbo-component-stage-{today}.parquet",
    },
    {
        "mssql_table": "dbo.ComponentVerified",
        "parquet_path": paths.REPO_DIR / f"dbo-component-verified-{today}.parquet",
    },
    {
        "mssql_table": "dbo.EmailTemplate",
        "parquet_path": paths.REPO_DIR / f"dbo-email-template-{today}.parquet",
    },
    {
        "mssql_table": "dbo.EmailType",
        "parquet_path": paths.REPO_DIR / f"dbo-email-type-{today}.parquet",
    },
    {
        "mssql_table": "dbo.InputType",
        "parquet_path": paths.REPO_DIR / f"dbo-input-type-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Language",
        "parquet_path": paths.REPO_DIR / f"dbo-language-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Operation",
        "parquet_path": paths.REPO_DIR / f"dbo-operation-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Product",
        "parquet_path": paths.REPO_DIR / f"dbo-product-{today}.parquet",
    },
    {
        "mssql_table": "dbo.ProductApproval",
        "parquet_path": paths.REPO_DIR / f"dbo-product-approval-{today}.parquet",
    },
    # {  # too big, and barely useful
    #     "mssql_table": "dbo.ProductAudit",
    #     "parquet_path": paths.REPO_DIR / f"dbo-product-audit-{today}.parquet",
    # },
    {
        "mssql_table": "dbo.ProductComponent",
        "parquet_path": paths.REPO_DIR / f"dbo-product-component-{today}.parquet",
    },
    {
        "mssql_table": "dbo.ProductEPR",
        "parquet_path": paths.REPO_DIR / f"dbo-product-epr-{today}.parquet",
        "custom_query": textwrap.dedent("""
            COPY (
              SELECT
                -- drop `RowVersion`, because MS SQL's explicitly forbids casting
                -- its `timestamp/rowversion` type (which is a binary) into
                -- anything useful
                * EXCLUDE (RowVersion)
                , current_timestamp AS EXPORTED_AT -- in UTC
              FROM mssql.{__MSSQL_TABLE__}
            ) TO '{__PARQUET_PATH__}' (FORMAT parquet)
            """).strip(),
    },
    {
        "mssql_table": "dbo.ProductPackaging",
        "parquet_path": paths.REPO_DIR / f"dbo-product-packaging-{today}.parquet",
        "custom_query": textwrap.dedent("""
            COPY (
              SELECT
                -- drop `RowVersion`, because MS SQL's explicitly forbids casting
                -- its `timestamp/rowversion` type (which is a binary) into
                -- anything useful
                * EXCLUDE (RowVersion)
                , current_timestamp AS EXPORTED_AT -- in UTC
              FROM mssql.{__MSSQL_TABLE__}
            ) TO '{__PARQUET_PATH__}' (FORMAT parquet)
            """).strip(),
    },
    {
        "mssql_table": "dbo.ProductStage",
        "parquet_path": paths.REPO_DIR / f"dbo-product-stage-{today}.parquet",
    },
    {
        "mssql_table": "dbo.ProductStatus",
        "parquet_path": paths.REPO_DIR / f"dbo-product-status-{today}.parquet",
    },
    {
        "mssql_table": "dbo.ProductVerified",
        "parquet_path": paths.REPO_DIR / f"dbo-product-verified-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Regulation",
        "parquet_path": paths.REPO_DIR / f"dbo-regulation-{today}.parquet",
    },
    {
        "mssql_table": "dbo.SendGridMessage",
        "parquet_path": paths.REPO_DIR / f"dbo-send-grid-message-{today}.parquet",
    },
    {
        "mssql_table": "dbo.SourceFile",
        "parquet_path": paths.REPO_DIR / f"dbo-source-file-{today}.parquet",
    },
    {
        "mssql_table": "dbo.SubmissionPeriod",
        "parquet_path": paths.REPO_DIR / f"dbo-submission-period-{today}.parquet",
    },
    {
        "mssql_table": "dbo.SupplierAlias",
        "parquet_path": paths.REPO_DIR / f"dbo-supplier-alias-{today}.parquet",
    },
    {
        "mssql_table": "dbo.Suppression",
        "parquet_path": paths.REPO_DIR / f"dbo-suppression-{today}.parquet",
    },
    {
        "mssql_table": "dbo.SuppressionReason",
        "parquet_path": paths.REPO_DIR / f"dbo-suppression-reason-{today}.parquet",
    },
    # {  # too big, and barely useful
    #     "mssql_table": "dbo.UserAudit",
    #     "parquet_path": paths.REPO_DIR / f"dbo-useraudit-{today}.parquet",
    # },
    {
        "mssql_table": "dbo.UserStatus",
        "parquet_path": paths.REPO_DIR / f"dbo-userstatus-{today}.parquet",
    },
    {
        "mssql_table": "epr.Country",
        "parquet_path": paths.REPO_DIR / f"epr-country-{today}.parquet",
    },
    {
        "mssql_table": "epr.DataCollectionMethodology",
        "parquet_path": paths.REPO_DIR
        / f"epr-data-collection-methodology-{today}.parquet",
    },
    {
        "mssql_table": "epr.ForestryCertification",
        "parquet_path": paths.REPO_DIR / f"epr-forestry-certification-{today}.parquet",
    },
    {
        "mssql_table": "epr.Oprl",
        "parquet_path": paths.REPO_DIR / f"epr-oprl-{today}.parquet",
    },
    {
        "mssql_table": "epr.PackagingClass",
        "parquet_path": paths.REPO_DIR / f"epr-packaging-class-{today}.parquet",
    },
    {
        "mssql_table": "epr.PackagingColour",
        "parquet_path": paths.REPO_DIR / f"epr-packaging-colour-{today}.parquet",
    },
    {
        "mssql_table": "epr.PackagingFormat",
        "parquet_path": paths.REPO_DIR / f"epr-packaging-format-{today}.parquet",
    },
    {
        "mssql_table": "epr.PackagingMaterial",
        "parquet_path": paths.REPO_DIR / f"epr-packaging-material-{today}.parquet",
    },
    {
        "mssql_table": "epr.ProductFamily",
        "parquet_path": paths.REPO_DIR / f"epr-product-family-{today}.parquet",
    },
    {
        "mssql_table": "epr.Ram",
        "parquet_path": paths.REPO_DIR / f"epr-ram-{today}.parquet",
    },
    {
        "mssql_table": "epr.RamSource",
        "parquet_path": paths.REPO_DIR / f"epr-ram-source-{today}.parquet",
    },
    {
        "mssql_table": "epr.RecycledContentType",
        "parquet_path": paths.REPO_DIR / f"epr-recycled-contenttype-{today}.parquet",
    },
]


def _render_sql_query(table: CollectTable) -> db.Sql:
    parquet_path = table["parquet_path"].expanduser().resolve()

    if query := table.get("custom_query"):
        query = query.replace("{__MSSQL_TABLE__}", table["mssql_table"])
        query = query.replace("{__PARQUET_PATH__}", str(parquet_path))
        return query

    query = textwrap.dedent(f"""
        COPY (
            SELECT
                *
                , current_timestamp AS EXPORTED_AT -- in UTC
            FROM mssql.{table["mssql_table"]}
        ) TO '{parquet_path}' (FORMAT parquet)
        """).strip()
    return query


def download_collect_data_from_azure_sql(
    config: Config, tables: list[CollectTable]
) -> None:
    checks.verify_azure_sql_firewall(config)

    logger.info("downloading data into parquet files")
    with db.DuckDb(config) as duckdb:
        for collect_table in tables:
            if collect_table["parquet_path"].exists():
                logger.info(f"file already downloaded: {collect_table['parquet_path']}")
                continue
            query = _render_sql_query(table=collect_table)
            duckdb.execute(query=query)


def download_collect_table_from_azure_sql(
    duckdb: db.DuckDb, table: CollectTable
) -> None:
    query = _render_sql_query(table=table)
    parquet_path = table["parquet_path"]
    if parquet_path.exists():
        logger.info(f"file already downloaded: {parquet_path}")
        return
    else:
        duckdb.execute(query=query)


def main(config: Config) -> None:
    if config.one_by_one:
        logger.info("processing tables one by one")
        checks.verify_azure_sql_firewall(config)
        with (
            db.DuckDb(config) as duckdb,
            connect_to_snowflake(
                account=config.snowflake_account,
                user=config.snowflake_user,
                password=config.snowflake_token,
                role=config.snowflake_role,
            ) as conn,
        ):
            snowflake._create_file_format_if_missing(config=config, conn=conn)
            snowflake._create_stage_if_missing(config=config, conn=conn)
            for table in COLLECT_TABLES:
                download_collect_table_from_azure_sql(duckdb=duckdb, table=table)
                snowflake.upload_collect_table(config=config, conn=conn, table=table)
    else:
        logger.info("processing all tables at once")
        download_collect_data_from_azure_sql(config=config, tables=COLLECT_TABLES)
        snowflake.upload_collect_tables(config=config, tables=COLLECT_TABLES)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs.")
    parser.add_argument(
        "--one-by-one",
        action="store_true",
        help="Download and upload each table before processing the next one.",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    )
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("snowflake").setLevel(logging.WARNING)

    config = Config.from_environment().extend(one_by_one=args.one_by_one)
    logger.debug(f"{config=}")

    main(config=config)
