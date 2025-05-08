from dashboard.container import Singleton, container


def jsonify_needed_columns(record):
    """
    Wrapper for JSONB type columns.
    """
    from psycopg2.extras import Json

    if isinstance(record, list):
        return [jsonify_needed_columns(r) for r in record]
    elif isinstance(record, dict):
        return {
            key: Json(value) if isinstance(value, dict) else value
            for key, value in record.items()
        }
    else:
        return record


class DBClient(metaclass=Singleton):
    def __init__(self, test_db_engine=None, supabase_client=None):
        self.test_db_engine = test_db_engine
        self.supabase_client = supabase_client or container.get("SUPABASE_CLI")

    def call_rpc(self, fn_name: str, params: dict):
        if self.test_db_engine is not None:
            import sqlalchemy

            placeholders = ", ".join(":" + key for key in params.keys())
            query = sqlalchemy.text(f"SELECT * FROM public.{fn_name}({placeholders})")
            with self.test_db_engine.connect() as conn:
                result = conn.execute(query, params)
                return result.mappings().all()
        else:
            response = self.supabase_client.rpc(fn_name, params).execute()
            return response.data

    def insert_into_table(self, table: str, record):
        if self.test_db_engine is not None:
            import sqlalchemy

            record = jsonify_needed_columns(record)
            if isinstance(record, list):
                keys = record[0].keys()
                columns = ", ".join(keys)
                placeholders = ", ".join(":" + key for key in keys)
                query = sqlalchemy.text(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                )
                with self.test_db_engine.begin() as conn:
                    result = conn.execute(query, record)
                    return result.rowcount
            else:
                columns = ", ".join(record.keys())
                placeholders = ", ".join(":" + key for key in record.keys())
                query = sqlalchemy.text(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                )
                with self.test_db_engine.begin() as conn:
                    result = conn.execute(query, record)
                    return result.rowcount
        else:
            response = self.supabase_client.table(table).insert(record).execute()
            return response.data

    def _apply_conditions(self, query_builder, conditions: dict):
        """Helper method to consistently apply conditions across all query types"""
        for key, value in conditions.items():
            if value is None:
                query_builder = query_builder.is_(key, None)
            elif isinstance(value, (list, tuple)):
                query_builder = query_builder.in_(key, value)
            else:
                query_builder = query_builder.eq(key, value)
        return query_builder

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
    ):
        conditions = conditions or {}

        if self.test_db_engine is not None:
            import sqlalchemy

            query = f"SELECT {select_columns} FROM {table}"
            if conditions:
                cond_str = " AND ".join(
                    [f"{key} = :{key}" for key in conditions.keys()]
                )
                query += f" WHERE {cond_str}"
            if order_by:
                query += f" ORDER BY {order_by}"
                if desc:
                    query += " DESC"
            if limit:
                query += f" LIMIT {limit}"
            sql_query = sqlalchemy.text(query)
            with self.test_db_engine.connect() as conn:
                result = conn.execute(sql_query, conditions)
                rows = result.mappings().all()
            if single:
                return rows[0]
            elif maybe_single:
                return rows[0] if rows else None
            return rows
        else:
            query_builder = self.supabase_client.table(table).select(select_columns)
            query_builder = self._apply_conditions(query_builder, conditions)
            if order_by:
                query_builder = query_builder.order(order_by, desc=desc)
            if limit:
                query_builder = query_builder.limit(limit)
            if maybe_single:
                query_builder = query_builder.maybe_single()
                response = query_builder.execute()
                if response is None:
                    return None
            elif single:
                query_builder = query_builder.single()
            response = query_builder.execute()
            return response.data

    def delete_from_table(self, table: str, conditions: dict):
        if self.test_db_engine is not None:
            import sqlalchemy

            query = f"DELETE FROM {table}"
            if conditions:
                cond_str = " AND ".join(
                    [f"{key} = :{key}" for key in conditions.keys()]
                )
                query += f" WHERE {cond_str}"
            sql_query = sqlalchemy.text(query)
            with self.test_db_engine.begin() as conn:
                result = conn.execute(sql_query, conditions)
                return result.rowcount
        else:
            query_builder = self.supabase_client.table(table).delete()
            query_builder = self._apply_conditions(query_builder, conditions)

            response = query_builder.execute()
            return bool(response.data)

    def update_table(self, table: str, record: dict, conditions: dict):
        if self.test_db_engine is not None:
            import sqlalchemy

            set_str = ", ".join(f"{key} = :{key}" for key in record.keys())
            where_str = " AND ".join(
                f"{key} = :cond_{key}" for key in conditions.keys()
            )
            query = sqlalchemy.text(f"UPDATE {table} SET {set_str} WHERE {where_str}")
            params = record.copy()
            for key, value in conditions.items():
                params[f"cond_{key}"] = value
            with self.test_db_engine.begin() as conn:
                result = conn.execute(query, params)
                return result.rowcount
        else:
            query_builder = self.supabase_client.table(table).update(record)
            query_builder = self._apply_conditions(query_builder, conditions)
            response = query_builder.execute()
            return response.data
