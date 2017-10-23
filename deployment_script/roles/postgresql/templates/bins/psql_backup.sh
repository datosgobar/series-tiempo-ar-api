#!/usr/bin/env bash

today=`date +%Y-%m-%d.%H:%M:%S`
export PGUSER="{{ postgresql_user }}"
export PGPASSWORD="{{ postgresql_password }}"
export PGDATABASE="{{ postgresql_database_name }}"
BACKUP_FILE="$PGDATABASE"_backup_"$today".dump

temp_dir=$(mktemp -d)
TMP_FILE=$temp_dir/$BACKUP_FILE

pg_dump -Fc "$PGDATABASE" > $TMP_FILE
BACKUP_PATH="{{ postgresql_backup_dir }}$BACKUP_FILE"
cp $TMP_FILE $BACKUP_PATH
chmod 0660 $BACKUP_PATH