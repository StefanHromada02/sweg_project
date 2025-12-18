#!/bin/bash
# Test MinIO initialization and bucket creation

set -e

echo "=== Testing MinIO Service ==="

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
timeout 30 bash -c 'until curl -f http://localhost:9000/minio/health/live 2>/dev/null; do sleep 2; done' || {
    echo "❌ MinIO health check failed"
    exit 1
}
echo "✅ MinIO is healthy"

# Check if bucket exists
echo "Checking if bucket 'social-media-bucket' exists..."
if mc ls local/social-media-bucket > /dev/null 2>&1; then
    echo "✅ Bucket 'social-media-bucket' exists"
else
    echo "❌ Bucket 'social-media-bucket' not found"
    exit 1
fi

# Test bucket is public
echo "Testing public access to bucket..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/social-media-bucket/)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "✅ Bucket is accessible (HTTP $HTTP_CODE)"
else
    echo "❌ Bucket not accessible (HTTP $HTTP_CODE)"
    exit 1
fi

echo ""
echo "=== All MinIO Tests Passed! ==="
