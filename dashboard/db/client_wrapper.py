import os

import sqlalchemy
from psycopg2.extras import Json
from supabase import Client, create_client

from dashboard.db.client import supabase_cli


def wrap_json_columns(record):
    """
    Wrapper for JSONB type columns.
    """
    if isinstance(record, list):
        return [wrap_json_columns(r) for r in record]
    elif isinstance(record, dict):
        return {
            key: Json(value) if isinstance(value, dict) else value
            for key, value in record.items()
        }
    else:
        return record


class DBClient:
    def __init__(self, test_db_engine=None):
        self.test_db_engine = test_db_engine

    def call_rpc(self, fn_name: str, params: dict):
        if os.environ.get("TESTING", "false").lower() == "true":
            if self.test_db_engine is None:
                raise ValueError(
                    "Test db engine should be accessible in testing environment!"
                )
            placeholders = ", ".join(":" + key for key in params.keys())
            query = sqlalchemy.text(f"SELECT * FROM public.{fn_name}({placeholders})")
            with self.test_db_engine.connect() as conn:
                result = conn.execute(query, **params)
                return result.fetchall()
        else:
            response = supabase_cli.rpc(fn_name, params).execute()
            return response.data

    def insert_into_table(self, table: str, record, db_engine=None):
        if (
            os.environ.get("TESTING", "false").lower() == "true"
            and db_engine is not None
        ):
            record = wrap_json_columns(record)
            if isinstance(record, list):
                keys = record[0].keys()
                columns = ", ".join(keys)
                placeholders = ", ".join(":" + key for key in keys)
                query = sqlalchemy.text(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                )
                with db_engine.begin() as conn:
                    result = conn.execute(query, record)
                    return result.rowcount
            else:
                columns = ", ".join(record.keys())
                placeholders = ", ".join(":" + key for key in record.keys())
                query = sqlalchemy.text(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                )
                with db_engine.begin() as conn:
                    result = conn.execute(query, record)
                    return result.rowcount
        else:
            response = supabase_cli.table(table).insert(record).execute()
            return response.data


DB_CLIENT = DBClient()  # @todo Create a singleton please
