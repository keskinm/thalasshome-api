import os

from supabase import Client, create_client

from dashboard.container import container

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase_cli: Client = create_client(url, key)
