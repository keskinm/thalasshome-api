# run.py
from dashboard.main import init_app

app = init_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
    '''
    ENTRY COMMAND:
    gunicorn -b 0.0.0.0:8000 dashboard.run:app
    '''

