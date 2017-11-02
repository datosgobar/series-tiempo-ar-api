#!/usr/bin/env bash


python manage.py test --stop --with-coverage --cover-branches  --cover-inclusive --cover-package=series_tiempo_ar_api --settings=conf.settings.testing --exclude=settings --exclude=migrations
