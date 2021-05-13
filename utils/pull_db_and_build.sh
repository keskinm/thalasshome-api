gcloud auth login
gcloud config set project employees-dashboard-307021
gcloud compute scp websocket-server:/home/spa_detente_france/providers.db ..

ZIP_FILE=../th.zip

if [ -f "$ZIP_FILE" ]; then
    rm "$ZIP_FILE"
else
    echo ""
fi

zip -r ../th.zip .. -x '*/venv/*'
