from __future__ import annotations

import os
from dataclasses import dataclass

type EnvironmentVariableName = str


def _read_environment_variable_as_string(name: EnvironmentVariableName) -> str:
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"expected {name!r} environment variable, but not found")

    clean_value = value.strip()
    if not clean_value:
        raise RuntimeError(
            f"expected {name!r} environment variable to be a non-empty string,"
            f" but got instead {value!r}"
        )

    return clean_value


@dataclass(frozen=True)
class EnvironmentConfig:
    sql_server: str
    sql_database: str
    snowflake_token: str
    snowflake_user: str
    snowflake_account: str
    snowflake_role: str
    snowflake_database: str
    snowflake_schema: str

    @staticmethod
    def from_environment() -> EnvironmentConfig:
        return EnvironmentConfig(
            sql_server=_read_environment_variable_as_string("AZURE_SQL_SERVER"),
            sql_database=_read_environment_variable_as_string("AZURE_SQL_DATABASE"),
            snowflake_token=_read_environment_variable_as_string("SNOWFLAKE_TOKEN"),
            snowflake_user=_read_environment_variable_as_string("SNOWFLAKE_USER"),
            snowflake_account=_read_environment_variable_as_string("SNOWFLAKE_ACCOUNT"),
            snowflake_role=_read_environment_variable_as_string("SNOWFLAKE_ROLE"),
            snowflake_database=_read_environment_variable_as_string(
                "SNOWFLAKE_DATABASE"
            ),
            snowflake_schema=_read_environment_variable_as_string("SNOWFLAKE_SCHEMA"),
        )

    def extend(self, one_by_one: bool) -> Config:
        return Config(**self.__dict__, one_by_one=one_by_one)


@dataclass(frozen=True)
class Config(EnvironmentConfig):
    one_by_one: bool
