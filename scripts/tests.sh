#!/usr/bin/env bash

python scripts/http_server.py &

SERVER_PID=$!

python manage.py test --stop --with-coverage --cover-branches  --cover-inclusive --cover-package=series_tiempo_ar_api --settings=conf.settings.testing --exclude=settings --exclude=migrations

EXIT_CODE=$?

kill -KILL $SERVER_PID

exit $EXIT_CODE
