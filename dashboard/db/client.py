import os

import sqlalchemy
from supabase import Client, create_client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase_cli: Client = create_client(url, key)


def call_rpc(fn_name: str, params: dict, db_engine=None):
    if os.environ.get("TESTING", "false").lower() == "true" and db_engine is not None:
        placeholders = ", ".join(":" + key for key in params.keys())
        query = sqlalchemy.text(f"SELECT * FROM public.{fn_name}({placeholders})")
        with db_engine.connect() as conn:
            result = conn.execute(query, **params)
            return result.fetchall()
    else:
        response = supabase_cli.rpc(fn_name, params).execute()
        return response.data


def select_from_table(
    table: str,
    select_columns: str = "*",
    conditions: dict = None,
    limit: int = None,
    single: bool = False,
    db_engine=None,
):
    conditions = conditions or {}

    if os.environ.get("TESTING", "false").lower() == "true" and db_engine is not None:
        query = f"SELECT {select_columns} FROM {table}"
        if conditions:
            cond_str = " AND ".join([f"{key} = :{key}" for key in conditions.keys()])
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
