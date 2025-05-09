from typing import Any, Dict, List, Optional, Union

import sqlalchemy

from dashboard.db.base import DBClientInterface
from dashboard.db.utils import jsonify_needed_columns


class TestDBClient(DBClientInterface):
    def __init__(self, db_engine):
        self.engine = db_engine
        self._connection = None
        self._transaction = None

    def begin(self):
        if not self._connection:
            self._connection = self.engine.connect()
            self._transaction = self._connection.begin()

    def commit(self):
        if self._transaction:
            self._transaction.commit()
            self._connection.close()
            self._transaction = None
            self._connection = None

    def rollback(self):
        if self._transaction:
            self._transaction.rollback()
            self._connection.close()
            self._transaction = None
            self._connection = None

    def get_connection(self):
        return self._connection or self.engine.connect()

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
        conn = self.get_connection()
        result = conn.execute(sql_query, conditions)
        rows = result.mappings().all()
        if maybe_single:
            return rows[0] if rows else None
        elif single:
            return rows[0]
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
            conn = self.get_connection()
            result = conn.execute(query, record)
            return result.rowcount
        else:
            columns = ", ".join(record.keys())
            placeholders = ", ".join(":" + key for key in record.keys())
            query = sqlalchemy.text(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            )
            conn = self.get_connection()
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
        conn = self.get_connection()
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
        conn = self.get_connection()
        result = conn.execute(sql_query, conditions)
        return result.rowcount

    def call_rpc(self, fn_name: str, params: dict) -> Any:
        placeholders = ", ".join(":" + key for key in params.keys())
        query = sqlalchemy.text(f"SELECT * FROM public.{fn_name}({placeholders})")
        conn = self.get_connection()
        result = conn.execute(query, params)
        return result.mappings().all()

    def upsert_into_table(
        self,
        table: str,
        record: Union[Dict, List[Dict]],
        unique_columns: List[str],
    ) -> Any:
        if isinstance(record, dict):
            records = [record]
        else:
            records = record

        results = []
        conn = self.get_connection()

        for item in records:
            # Build the ON CONFLICT clause
            conflict_target = ", ".join(unique_columns)
            update_columns = [k for k in item.keys() if k not in unique_columns]
            update_set = ", ".join(f"{k} = EXCLUDED.{k}" for k in update_columns)

            columns = ", ".join(item.keys())
            placeholders = ", ".join(":" + key for key in item.keys())

            query = sqlalchemy.text(
                f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_target})
                DO UPDATE SET {update_set}
                """
            )

            result = conn.execute(query, item)
            results.append(result.rowcount)

        return sum(results)
