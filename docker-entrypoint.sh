#!/bin/sh
set -e

# Determine database host and port
if [ -n "$DATABASE_URL" ]; then
    db_host=$(echo "$DATABASE_URL" | sed -e 's|.*@||' -e 's|:.*||')
    db_port=$(echo "$DATABASE_URL" | sed -e 's|.*:||' -e 's|/.*||')
else
    db_host=${DATABASE_HOST:-db}
    db_port=${DATABASE_PORT:-5432}
fi

printf 'Waiting for database at %s:%s...\n' "$db_host" "$db_port"
while ! nc -z "$db_host" "$db_port"; do
    sleep 1
    printf '.'
done
printf '\nDatabase is available. Applying migrations...\n'

python manage.py migrate --noinput

exec "$@"
