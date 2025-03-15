from dashboard.container import container
from dashboard.db.client import supabase_cli

container.register_singleton("supabase_cli", supabase_cli)

from dashboard.db.client_wrapper import DBClient

container.register_singleton("DB_CLIENT", DBClient())

EOF_REGISTERER = True
