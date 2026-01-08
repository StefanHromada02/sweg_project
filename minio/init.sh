#!/bin/sh

set -e

# MinIO starten (im Hintergrund)
minio "$@" &
MINIO_PID=$!

# Warten bis MinIO erreichbar ist
echo "Waiting for MinIO to start..."
until curl -s http://localhost:9000/minio/health/ready; do
    sleep 1
done

echo "MinIO is up – configuring..."

# MinIO Client installieren (mc)
mc alias set local http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

# Bucket erstellen, falls er nicht existiert
mc mb --ignore-existing local/social-media-bucket

# Public Policy setzen
mc anonymous set public local/social-media-bucket

echo "Public bucket 'social-media-bucket' is ready!"

# Foreground laufen lassen
wait $MINIO_PID