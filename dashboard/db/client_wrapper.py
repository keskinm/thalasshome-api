import os

import sqlalchemy
from psycopg2.extras import Json

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
        if os.environ.get("TESTING", "false").lower() == "true":
            if self.test_db_engine is None:
                raise ValueError(
                    "Test db engine should be accessible in testing environment!"
                )
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

    def select_from_table(
        self,
        table: str,
        select_columns: str = "*",
        conditions: dict = None,
        limit: int = None,
        single: bool = False,
        db_engine=None,
    ):
        conditions = conditions or {}

        if os.environ.get("TESTING", "false").lower() == "true":
            if self.test_db_engine is None:
                raise ValueError(
                    "Test db engine should be accessible in testing environment!"
                )

            query = f"SELECT {select_columns} FROM {table}"
            if conditions:
                cond_str = " AND ".join(
                    [f"{key} = :{key}" for key in conditions.keys()]
                )
                query += f" WHERE {cond_str}"
            if limit:
                query += f" LIMIT {limit}"
            sql_query = sqlalchemy.text(query)
            with db_engine.connect() as conn:
                result = conn.execute(sql_query, **conditions)
                rows = result.fetchall()
            if single:
                return rows[0] if rows else None
            return rows
        else:
            query_builder = supabase_cli.table(table).select(select_columns)
            for key, value in conditions.items():
                query_builder = query_builder.eq(key, value)
            if limit:
                query_builder = query_builder.limit(limit)
            if single:
                query_builder = query_builder.single()
            response = query_builder.execute()
            return response.data


DB_CLIENT = DBClient()  # @todo Create a singleton please
