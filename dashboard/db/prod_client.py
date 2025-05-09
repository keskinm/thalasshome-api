from typing import Any, Dict, List, Optional, Union

from dashboard.db.base import DBClientInterface


class ProdDBClient(DBClientInterface):
    def __init__(self, supabase_client):
        self.supabase_client = supabase_client  # Fix: was using self.supabase instead of self.supabase_client

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
    ) -> Union[List[Dict], Dict, None]:
        conditions = conditions or {}
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

    def insert_into_table(
        self,
        table: str,
        values: Union[Dict, List[Dict]],
    ) -> Any:
        response = self.supabase_client.table(table).insert(values).execute()
        return response.data

    def update_table(
        self,
        table: str,
        record: Dict,
        conditions: Dict,
    ) -> Any:
        query_builder = self.supabase_client.table(table).update(record)
        query_builder = self._apply_conditions(query_builder, conditions)
        response = query_builder.execute()
        return response.data

    def delete_from_table(
        self,
        table: str,
        conditions: Dict,
    ) -> Any:
        query_builder = self.supabase_client.table(table).delete()
        query_builder = self._apply_conditions(query_builder, conditions)

        response = query_builder.execute()
        return bool(response.data)

    def call_rpc(
        self,
        function_name: str,
        params: Dict,
    ) -> Any:
        response = self.supabase_client.rpc(function_name, params).execute()
        return response.data

    def upsert_into_table(
        self,
        table: str,
        values: Union[Dict, List[Dict]],
        unique_columns: List[str],
    ) -> Any:
        response = (
            self.supabase_client.table(table)
            .upsert(values, on_conflict=",".join(unique_columns))
            .execute()
        )
        return response.data
