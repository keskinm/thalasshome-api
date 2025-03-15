import os

import sqlalchemy
from psycopg2.extras import Json

from dashboard.container import Singleton, container

supabase_cli = container.get("supabase_cli")


def jsonify_needed_columns(record):
    """
    Wrapper for JSONB type columns.
    """
    if isinstance(record, list):
        return [jsonify_needed_columns(r) for r in record]
    elif isinstance(record, dict):
        return {
            key: Json(value) if isinstance(value, dict) else value
            for key, value in record.items()
        }
    else:
        return record


def env_checker(method):
    def wrapped(*args, **kwargs):
        if not "_" in method.__name__:
            db_client = args[0]
            test_db_engine_is_none = db_client.test_db_engine is None
            is_test_env = os.environ.get("TESTING", "false").lower() == "true"
            if is_test_env and test_db_engine_is_none:
                raise ValueError(
                    "Test db engine should be accessible in testing environment!"
                )
            elif not is_test_env and not test_db_engine_is_none:
                raise ValueError(
                    "Test db engine should not be provided for execution environment!"
                )

        result = method(*args, **kwargs)
        return result

    return wrapped


def wrap_all_methods_with_env_checker(cls):
    """Class decorator to wrap all methods of a class with a decorator."""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value):
            setattr(cls, attr_name, env_checker(attr_value))
    return cls


@wrap_all_methods_with_env_checker
class DBClient(metaclass=Singleton):
    def __init__(self, test_db_engine=None):
        self.test_db_engine = test_db_engine

    def call_rpc(self, fn_name: str, params: dict):
        if self.test_db_engine is not None:
            placeholders = ", ".join(":" + key for key in params.keys())
            query = sqlalchemy.text(f"SELECT * FROM public.{fn_name}({placeholders})")
            with self.test_db_engine.connect() as conn:
                result = conn.execute(query, **params)
                return result.fetchall()
        else:
            response = supabase_cli.rpc(fn_name, params).execute()
            return response.data

    def insert_into_table(self, table: str, record, db_engine=None):
        if self.test_db_engine is not None:
            record = jsonify_needed_columns(record)
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

        if self.test_db_engine is not None:
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
