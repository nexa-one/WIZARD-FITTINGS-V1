#!/bin/sh
# Drops and re-creates all tables via Alembic – USE WITH CAUTION (dev only)
set -e
echo "WARNING: This will destroy all data in the database!"
read -p "Type 'yes' to continue: " confirm
[ "$confirm" = "yes" ] || exit 1

docker exec cfm_backend alembic downgrade base
docker exec cfm_backend alembic upgrade head
echo "Database reset complete."
