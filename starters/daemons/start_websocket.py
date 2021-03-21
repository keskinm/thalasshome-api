import os


os.system('sudo chmod +x env.sh | '
          'sudo chmod +x local_env.sh | '
          '. ../../env.sh | '
          '. ../../local_env.sh | '
          'gunicorn -b 0.0.0.0:1337 websocket.ws:app --worker-class sanic.worker.GunicornWorker --daemon')

