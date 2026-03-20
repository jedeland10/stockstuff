#!/bin/bash
# Daily PostgreSQL backup — run via cron
# Keeps last 7 daily backups

BACKUP_DIR="/home/stonklens/backups"
COMPOSE_DIR="/home/stonklens"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAX_BACKUPS=2

mkdir -p "$BACKUP_DIR"

# Dump the database
docker compose -f "$COMPOSE_DIR/docker-compose.yml" exec -T db \
  pg_dump -U stockdata -d stockdata --no-owner --no-acl \
  | gzip > "$BACKUP_DIR/stockdata_$TIMESTAMP.sql.gz"

if [ $? -eq 0 ]; then
  echo "Backup created: stockdata_$TIMESTAMP.sql.gz ($(du -h "$BACKUP_DIR/stockdata_$TIMESTAMP.sql.gz" | cut -f1))"
else
  echo "Backup FAILED"
  exit 1
fi

# Remove old backups (keep last N)
ls -t "$BACKUP_DIR"/stockdata_*.sql.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
echo "Backups retained: $(ls "$BACKUP_DIR"/stockdata_*.sql.gz 2>/dev/null | wc -l)"
