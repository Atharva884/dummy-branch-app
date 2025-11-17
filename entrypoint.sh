echo "Starting API container with APP_ENV=$APP_ENV"

if [ "$APP_ENV" = "dev" ]; then
    echo "Running Flask in DEV mode..."
    exec flask run \
        --host=0.0.0.0 \
        --port="$PORT"
else
    echo "Running Gunicorn for STAGING/PROD..."
    exec gunicorn wsgi:app \
        -w "${API_WORKERS}" \
        --log-level "${LOG_LEVEL}" \
        --log-file - \
        --access-logfile - \
        --capture-output \
        --enable-stdio-inheritance \
        --access-logformat '{"time":"%(t)s","method":"%(m)s","path":"%(U)s","status":%(s)s,"bytes":%(B)s,"ua":"%(h)s"}' \
        -b "0.0.0.0:${PORT}"
fi
