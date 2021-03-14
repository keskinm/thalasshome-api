
ZIP_FILE=../th.zip

if [ -f "$ZIP_FILE" ]; then
    rm "$ZIP_FILE"
else
    echo ""
fi

zip -r ../th.zip .. -x '*/venv/*'
