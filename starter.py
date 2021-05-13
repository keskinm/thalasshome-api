import os
import argparse


def run(service, mode):
    if mode == 'local':
        daemon = '--daemon'
        env = """
        . env/local_passwords.sh
        . env/local_env.sh
            """
    else:
        daemon = ''
        env = """
        . env/env.sh
        . env/dev_env.sh
        . env/dev_passwords.sh
            """

    if service == 'websocket':
        serving = '0.0.0.0:1337 websocket.ws:app --worker-class sanic.worker.GunicornWorker'
    else:
        serving = '0.0.0.0:8000 dashboard.main:app'

    command = """
        gcloud auth login
        sudo chmod +x env/env.sh
        sudo chmod +x env/local_env.sh
        {env}
        gunicorn -b {serving} {daemon}
        """.format(serving=serving, env=env, daemon=daemon)

    print(command)

    # os.system(command)


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--service", type=str, choices=["websocket", "webserver"], default="websocket")
parser.add_argument("-m", "--mode", type=str, choices=["local", "dev"], default="dev")

kwargs = vars(parser.parse_args())
run(**kwargs)
