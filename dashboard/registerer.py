# isort: skip_file
import os

from supabase import create_client

from dashboard.container import container

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


container.register_singleton("supabase_cli", create_client(url, key))

from dashboard.db.client_wrapper import DBClient

container.register_singleton("DB_CLIENT", DBClient())

EOF_REGISTERER = True
