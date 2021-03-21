import os

os.system('sudo chmod +x env.sh | '
          'sudo chmod +x local_env.sh | '
          '. ../../env.sh | '
          '. ../../local_env.sh | '
          'gunicorn -b 0.0.0.0:8000 dashboard.main:app')

