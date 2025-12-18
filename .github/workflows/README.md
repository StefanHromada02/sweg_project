# GitHub Actions Workflows

This directory contains CI/CD workflows for the SWEG project.

## Workflows

### 1. CI - Test All Components ([ci.yml](ci.yml))
**Triggers:** Push to `main`, Pull Requests to `main`

Tests all individual components:
- **Backend Tests**: Python/Django unit tests with PostgreSQL and MinIO
  - Runs pytest on all backend tests
  - Lints code with flake8
  - Code coverage reporting

- **Frontend Tests**: Angular unit tests
  - Karma/Jasmine tests in headless Chrome
  - Builds production bundle
  - Tests with code coverage

- **Resize Service Tests**: Python worker validation
  - Lints the resize worker code
  - Validates Python syntax

### 2. Build and Push Docker Images ([docker-build-push.yml](docker-build-push.yml))
**Triggers:** 
- Push to `main` branch
- Git tags matching `v*.*.*`
- Manual workflow dispatch

Builds and pushes Docker images to GitHub Container Registry (ghcr.io) for:
- Backend (Django API)
- Frontend (Angular/Nginx)
- Resize Service (Python worker)
- MinIO (with custom init script)

**Image naming convention:**
```
ghcr.io/<your-username>/sweg-backend:latest
ghcr.io/<your-username>/sweg-backend:main
ghcr.io/<your-username>/sweg-backend:v1.0.0
ghcr.io/<your-username>/sweg-backend:main-<commit-sha>
```

**Features:**
- Multi-platform support via Docker Buildx
- Layer caching for faster builds
- Automatic tagging based on branches and semver tags
- Parallel builds for all services

### 3. Integration Tests ([integration-tests.yml](integration-tests.yml))
**Triggers:**
- Manual workflow dispatch
- Daily at 2 AM UTC (scheduled)

Runs full-stack integration tests:
- Builds and starts all services via docker-compose
- Tests service health endpoints
- Runs backend integration test suite
- Validates inter-service communication

## Setup Instructions

### For Docker Image Pushing

1. **Enable GitHub Packages** in your repository settings
2. **No additional secrets needed** - uses `GITHUB_TOKEN` automatically
3. Images will be pushed to `ghcr.io/<your-github-username>/sweg-*`

### Making Images Public (Optional)

By default, pushed images are private. To make them public:
1. Go to your GitHub profile → Packages
2. Select the package (e.g., `sweg-backend`)
3. Package settings → Change visibility → Public

### Using the Images

Pull images in your deployment:
```bash
docker pull ghcr.io/<username>/sweg-backend:latest
docker pull ghcr.io/<username>/sweg-frontend:latest
docker pull ghcr.io/<username>/sweg-resize-service:latest
docker pull ghcr.io/<username>/sweg-minio:latest
```

Update `compose.yaml` to use pre-built images:
```yaml
services:
  backend:
    image: ghcr.io/<username>/sweg-backend:latest
    # Remove the 'build' section
```

## Local Testing

Test workflows locally before pushing:

```bash
# Test backend locally
cd be
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest
flake8 --max-line-length=120 --exclude=migrations .

# Test frontend locally
cd fe/app
npm install
npm test
npm run build

# Test resize service
cd resize-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flake8 --max-line-length=120 resize_worker.py
```

## Workflow Status Badges

Add to your main README.md:

```markdown
![CI Tests](https://github.com/<username>/<repo>/actions/workflows/ci.yml/badge.svg)
![Docker Build](https://github.com/<username>/<repo>/actions/workflows/docker-build-push.yml/badge.svg)
```

## Troubleshooting

### Build failing on push
- Check the Actions tab for detailed logs
- Ensure all tests pass locally first
- Verify Dockerfiles are present and valid

### Docker images not pushing
- Check repository permissions (Settings → Actions → General)
- Ensure "Read and write permissions" is enabled for GITHUB_TOKEN
- Verify you're on the `main` branch or have created a version tag

### Integration tests timing out
- Services may need more startup time
- Increase sleep duration or health check retries
- Check docker-compose configuration matches .env template
