#!/usr/bin/env bash
/etc/init.d/mysql start
mysql < /app/init/1_db_ddl.sql
exec gunicorn --bind :8080 --workers 1 --threads 4 --timeout 0 app:app