# Social Media App - Backend (REST API)

Django REST Framework Backend für eine Social Media Applikation mit Post-Management, Bild-Upload und MinIO Object Storage.

## 🚀 Features

- **REST API** für Post-Management (CRUD Operations)
- **Bild-Upload** über MinIO Object Storage
- **Benutzer-Authentifizierung** (Django User Model)
- **OpenAPI/Swagger Documentation** via drf-spectacular
- **PostgreSQL** Datenbank
- **Docker & Docker Compose** Support
- **Umfassendes Testing Framework** (Unit Tests, Integration Tests)

## 📋 Voraussetzungen

- Docker & Docker Compose
- Python 3.12+ (für lokale Entwicklung)
- Git

## 🏗️ Projekt-Struktur

```
be/
├── config/              # Django Projekt-Konfiguration
│   ├── settings.py     # Hauptkonfiguration
│   ├── urls.py         # Root URL Configuration
│   └── wsgi.py/asgi.py # WSGI/ASGI Config
├── domains/
│   └── posts/          # Posts Domain
│       ├── models.py   # Post Model
│       ├── serializers.py  # DRF Serializers
│       ├── views.py    # API ViewSets
│       ├── urls.py     # Post URLs
│       └── tests/      # Test Suite
│           ├── test_models.py
│           ├── test_serializers.py
│           ├── test_views.py
│           └── test_integration.py
├── services/
│   └── minio_storage.py  # MinIO Integration
├── Dockerfile
├── entrypoint.sh       # Container Startup Script
├── requirements.txt
└── manage.py
```

## 🔧 Setup & Installation

### Option 1: Docker Compose (Empfohlen)

1. **Erstelle `.env` Datei im Root-Verzeichnis:**

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=social_media_db

# MinIO
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=minio_admin
```

2. **Starte alle Services:**

```bash
docker-compose up --build
```

3. **Die Anwendung ist verfügbar unter:**
   - Backend API: http://localhost:8000
   - API Dokumentation (Swagger): http://localhost:8000/api/schema/swagger-ui/
   - MinIO Console: http://localhost:9001

### Option 2: Lokale Entwicklung

1. **Erstelle Virtual Environment:**

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Installiere Dependencies:**

```bash
cd be
pip install -r requirements.txt
```

3. **Konfiguriere Umgebungsvariablen:**

Setze die notwendigen Environment Variables oder erstelle eine `.env` Datei.

4. **Führe Migrationen aus:**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Erstelle Superuser (optional):**

```bash
python manage.py createsuperuser
```

6. **Starte Development Server:**

```bash
python manage.py runserver
```

## 📚 API Endpunkte

### Posts

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/posts/` | Alle Posts abrufen |
| GET | `/api/posts/?author=<username>` | Posts nach Autor filtern |
| GET | `/api/posts/?search=<query>` | Posts durchsuchen |
| GET | `/api/posts/{id}/` | Einzelnen Post abrufen |
| POST | `/api/posts/` | Neuen Post erstellen |
| PUT/PATCH | `/api/posts/{id}/` | Post aktualisieren |
| DELETE | `/api/posts/{id}/` | Post löschen |

### Beispiel POST Request:

```bash
# Mit Bild
curl -X POST http://localhost:8000/api/posts/ \
  -F "content=Mein erster Post!" \
  -F "author=1" \
  -F "image=@/path/to/image.jpg"

# Ohne Bild
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Mein Post", "author": 1}'
```

### OpenAPI/Swagger Dokumentation

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema (JSON)**: http://localhost:8000/api/schema/

## 🧪 Testing

Das Projekt enthält ein umfassendes Test-Framework mit Unit- und Integration-Tests.

### Tests ausführen

**In Docker Container:**

```bash
# Alle Tests
docker-compose exec backend python manage.py test

# Nur Post Tests
docker-compose exec backend python manage.py test domains.posts.tests

# Spezifische Test-Datei
docker-compose exec backend python manage.py test domains.posts.tests.test_views

# Mit Verbose Output
docker-compose exec backend python manage.py test --verbosity=2
```

**Lokal:**

```bash
# Alle Tests
python manage.py test

# Nur bestimmte Tests
python manage.py test domains.posts.tests.test_integration

# Mit Coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Erstellt HTML Report in htmlcov/
```

### Test-Struktur

```
domains/posts/tests/
├── test_models.py       # Post Model Tests
├── test_serializers.py  # Serializer Tests
├── test_views.py        # ViewSet/API Tests
└── test_integration.py  # End-to-End Integration Tests
```

### Test Coverage

- **Models**: PostModel, PostManager (Custom Manager)
- **Serializers**: PostSerializer mit Bild-Upload
- **Views**: PostViewSet (CRUD, Filtering, Search)
- **Integration**: Full API Workflow Tests

## 🗄️ Datenbank

### Migrationen erstellen und anwenden:

```bash
# In Docker
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Lokal
python manage.py makemigrations
python manage.py migrate
```

### Datenbank zurücksetzen:

```bash
docker-compose down -v
docker-compose up --build
```

## 📦 MinIO Object Storage

MinIO wird für Bild-Uploads verwendet.

**MinIO Console Zugriff:**
- URL: http://localhost:9001
- Username: minioadmin (aus .env)
- Password: minioadmin123 (aus .env)

**Bucket**: `social-media-images` (wird automatisch erstellt)

## 🐛 Debugging

### Logs anzeigen:

```bash
# Alle Services
docker-compose logs -f

# Nur Backend
docker-compose logs -f backend

# Letzte 100 Zeilen
docker-compose logs --tail=100 backend
```

### In Container einsteigen:

```bash
docker-compose exec backend sh
```

### Django Shell:

```bash
# In Docker
docker-compose exec backend python manage.py shell

# Lokal
python manage.py shell
```

## 🔒 Sicherheit

- **CORS**: Konfiguriere CORS für Frontend-Zugriff in `settings.py`
- **SECRET_KEY**: Nutze Umgebungsvariablen für Production
- **DEBUG**: Setze `DEBUG=False` in Production
- **ALLOWED_HOSTS**: Konfiguriere in Production

## 🚢 Deployment

1. Setze `DEBUG=False` in settings.py
2. Konfiguriere `ALLOWED_HOSTS`
3. Nutze starke Passwörter in `.env`
4. Implementiere HTTPS
5. Konfiguriere Static File Serving (z.B. mit nginx)

## 📝 Git Workflow

```bash
# Feature Branch erstellen
git checkout -b feature/neue-funktion

# Änderungen committen
git add .
git commit -m "feat: Beschreibung der Änderung"

# Push und Pull Request
git push origin feature/neue-funktion
```

## 🔗 Nützliche Befehle

### Standard-Workflow (nach Code-Änderungen):
1. Container neu bauen und starten
docker-compose up -d --build

2. Warten bis Container bereit sind
Start-Sleep -Seconds 10

3. Migrationen erstellen und anwenden
docker exec -it social-media-backend python manage.py makemigrations
docker exec -it social-media-backend python manage.py migrate
### Bei Datenbank-Problemen
1. Alles stoppen UND Datenbank löschen
docker-compose down -v

2. Neu bauen und starten
docker-compose up -d --build

3. Warten
Start-Sleep -Seconds 15

4. Migrationen
docker exec -it social-media-backend python manage.py makemigrations
docker exec -it social-media-backend python manage.py migrate

```bash
# Container neu bauen
docker-compose up --build

# Container stoppen
docker-compose down

# Container + Volumes löschen
docker-compose down -v

# Superuser erstellen
docker-compose exec backend python manage.py createsuperuser

# Static Files sammeln
docker-compose exec backend python manage.py collectstatic --noinput
```

## 📖 Weitere Ressourcen

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/minio-py.html)

## 👥 Team

Entwickelt als Teil des SWEG Projekts.

## 📄 Lizenz

Dieses Projekt ist für Bildungszwecke erstellt.


