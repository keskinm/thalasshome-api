# isort: skip_file
import os

from supabase import create_client

from dashboard.container import container

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase_client = create_client(url, key)
container.register_singleton("SUPABASE_CLI", supabase_client)

from dashboard.db.prod_client import ProdDBClient

container.register_singleton("DB_CLIENT", ProdDBClient(supabase_client=supabase_client))

EOF_REGISTERER = True
