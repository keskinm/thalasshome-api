import os

import sqlalchemy
from psycopg2.extras import Json
from supabase import Client, create_client

from dashboard.db.client import supabase_cli


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


DB_CLIENT = DBClient()  # @todo Create a singleton please
