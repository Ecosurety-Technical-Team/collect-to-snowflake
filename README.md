Download Collect app data to your machine and push it Snowflake.

## Install

Note: this repo is designed to be used in Linux/Mac/WSL.

1. Clone the repo and build the container:

    ```shell
    git clone ...
    cd collect-to-snowflake
    docker compose build   # first run might take some time
    ```
    Note: you might need to turn Ecosurety's VPN off to fetch the container base image.

2. Get fresh Azure credentials inside the container:

    ```shell
    docker compose run --rm collect-to-snowflake az login --use-device-code
    ```

## Usage

Reminder: the Ecosurety VPN must be on to reach the Azure SQL database.

```shell
export AZURE_SQL_SERVER='...'
export AZURE_SQL_DATABASE='...'
export SNOWFLAKE_ACCOUNT='...'
export SNOWFLAKE_USER='...'
export SNOWFLAKE_TOKEN='...'
export SNOWFLAKE_ROLE='...'
export SNOWFLAKE_DATABASE='...'
export SNOWFLAKE_SCHEMA='...'
docker compose run --rm collect-to-snowflake
```

## Development

```shell
docker compose run --rm collect-to-snowflake-dev bash
```
