from __future__ import annotations

import json
import logging
import struct
import subprocess

import pyodbc

from src.config import Config

logger = logging.getLogger(__name__)


class AzureSqlFirewallRejectedConnection(ConnectionError):
    """Raised when Azure SQL rejects the client's network address."""


def verify_azure_sql_firewall(config: Config) -> None:
    """Verify that the current network can connect to Azure SQL.

    Uses the container's Azure CLI credentials and Microsoft ODBC Driver 18
    to perform a real token-authenticated connection.
    """
    logger.debug("obtaining an Azure access token")
    token = json.loads(
        subprocess.check_output(
            [
                "az",
                "account",
                "get-access-token",
                "--resource",
                "https://database.windows.net/",
                "--output",
                "json",
            ],
            text=True,
        )
    )["accessToken"]

    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack("<I", len(token_bytes)) + token_bytes
    connection_string = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server={config.sql_server};"
        f"Database={config.sql_database};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    logger.debug("connecting to Azure SQL")
    try:
        connection = pyodbc.connect(
            connection_string,
            attrs_before={1256: token_struct},
            timeout=10,
        )
    except pyodbc.Error as error:
        message = str(error).lower()
        if "40615" in message or ("firewall" in message and "not allowed" in message):
            raise AzureSqlFirewallRejectedConnection(
                "Azure SQL rejected this network connection. "
                "Connect to the company VPN and try again."
            ) from error
        raise
    else:
        connection.close()
