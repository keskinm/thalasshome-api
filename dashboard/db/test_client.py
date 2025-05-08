from typing import Any, Dict, List, Optional, Union

import sqlalchemy

from dashboard.db.base import DBClientInterface
from dashboard.db.utils import jsonify_needed_columns


class TestDBClient(DBClientInterface):
    def __init__(self, db_engine):
        self.engine = db_engine

    def select_from_table(
        self,
        table: str,
        select_columns: str = "*",
        conditions: dict = None,
        limit: int = None,
        single: bool = False,
        maybe_single: bool = False,
        order_by: str = None,
        desc: bool = False,
    ) -> Union[List[Dict], Dict, None]:
        conditions = conditions or {}
        query = f"SELECT {select_columns} FROM {table}"
        if conditions:
            cond_str = " AND ".join([f"{key} = :{key}" for key in conditions.keys()])
            query += f" WHERE {cond_str}"
        if order_by:
            query += f" ORDER BY {order_by}"
            if desc:
                query += " DESC"
        if limit:
            query += f" LIMIT {limit}"
        sql_query = sqlalchemy.text(query)
        with self.engine.connect() as conn:
            result = conn.execute(sql_query, conditions)
            rows = result.mappings().all()
        if single:
            return rows[0]
        elif maybe_single:
            return rows[0] if rows else None
        return rows

    def insert_into_table(
        self,
        table: str,
        record: Union[Dict, List[Dict]],
    ) -> Any:
        record = jsonify_needed_columns(record)
        if isinstance(record, list):
            keys = record[0].keys()
            columns = ", ".join(keys)
            placeholders = ", ".join(":" + key for key in keys)
            query = sqlalchemy.text(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            )
            with self.engine.begin() as conn:
                result = conn.execute(query, record)
                return result.rowcount
        else:
            columns = ", ".join(record.keys())
            placeholders = ", ".join(":" + key for key in record.keys())
            query = sqlalchemy.text(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            )
            with self.engine.begin() as conn:
                result = conn.execute(query, record)
                return result.rowcount

    def update_table(
        self,
        table: str,
        record: Dict,
        conditions: Dict,
    ) -> Any:
        set_str = ", ".join(f"{key} = :{key}" for key in record.keys())
        where_str = " AND ".join(f"{key} = :cond_{key}" for key in conditions.keys())
        query = sqlalchemy.text(f"UPDATE {table} SET {set_str} WHERE {where_str}")
        params = record.copy()
        for key, value in conditions.items():
            params[f"cond_{key}"] = value
        with self.engine.begin() as conn:
            result = conn.execute(query, params)
            return result.rowcount

    def delete_from_table(
        self,
        table: str,
        conditions: Dict,
    ) -> Any:
        query = f"DELETE FROM {table}"
        if conditions:
            cond_str = " AND ".join([f"{key} = :{key}" for key in conditions.keys()])
            query += f" WHERE {cond_str}"
        sql_query = sqlalchemy.text(query)
        with self.engine.begin() as conn:
            result = conn.execute(sql_query, conditions)
            return result.rowcount

    def call_rpc(self, fn_name: str, params: dict) -> Any:
        placeholders = ", ".join(":" + key for key in params.keys())
        query = sqlalchemy.text(f"SELECT * FROM public.{fn_name}({placeholders})")
        with self.engine.connect() as conn:
            result = conn.execute(query, params)
            return result.mappings().all()
