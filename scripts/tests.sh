#!/usr/bin/env bash

python scripts/http_server.py &

SERVER_PID=$!

python manage.py test --stop --settings=conf.settings.testing --exclude=settings --exclude=migrations $@

EXIT_CODE=$?

kill -KILL $SERVER_PID

exit $EXIT_CODE
