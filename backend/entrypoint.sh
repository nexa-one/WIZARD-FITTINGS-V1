#!/bin/sh
set -e

echo "CFM Fittings Pro – Backend Starting"
echo "Environment: ${APP_ENV:-development}"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until python3 -c "
import asyncio, asyncpg
async def check():
    conn = await asyncpg.connect(
        host='${POSTGRES_HOST:-cfm_postgres}',
        port=${POSTGRES_PORT:-5432},
        user='${POSTGRES_USER:-cfm_user}',
        password='${POSTGRES_PASSWORD:-cfm_secure_password_change_in_production}',
        database='${POSTGRES_DB:-cfm_fittings}',
    )
    await conn.close()
asyncio.run(check())
" 2>/dev/null; do
    echo "PostgreSQL not ready – retrying in 2s..."
    sleep 2
done

echo "PostgreSQL is ready."

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head

echo "Migrations complete. Starting server..."
exec "$@"
