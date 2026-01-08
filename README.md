# SWEG Social Media Project

A Django REST API backend for a social media platform with support for users, posts, and comments. Built with Django REST Framework, PostgreSQL, and MinIO for object storage.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Testing with Postman](#testing-with-postman)
- [Development](#development)

## ✨ Features

- **Users Management**: Create and manage user profiles with study programs and interests
- **Posts**: Create, read, update, and delete posts with image uploads
- **Comments**: Comment on posts with user attribution
- **Image Storage**: MinIO object storage for media files
- **API Documentation**: Auto-generated Swagger/ReDoc documentation
- **Search & Filtering**: Full-text search and filtering capabilities
- **PostgreSQL Database**: Robust relational database with foreign key relationships

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or higher)
- [Postman](https://www.postman.com/downloads/) (for API testing)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SWEG_project
```

### 2. Create Environment File

Create a `.env` file in the project root directory with the following variables:

```env
# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=social_media_db

# MinIO Configuration
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=minio_admin
```

### 3. Start the Services

```bash
docker-compose up -d
```

This will start:
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **MinIO Console**: http://localhost:9001
- **MinIO API**: http://localhost:9000

### 4. Run Database Migrations

```bash
docker exec -it social-media-backend python manage.py makemigrations
docker exec -it social-media-backend python manage.py migrate
```

### 5. Create Admin User (Optional)

```bash
docker exec -it social-media-backend python manage.py createsuperuser
```

### 6. Access the Application

- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **MinIO Console**: http://localhost:9001 (login with minio/minio_admin)

## 📁 Project Structure

```
SWEG_project/
├── be/                          # Backend (Django)
│   ├── config/                  # Django project configuration
│   │   ├── settings.py         # Main settings file
│   │   ├── urls.py             # Root URL configuration
│   │   └── wsgi.py             # WSGI application
│   │
│   ├── domains/                 # Domain-driven design structure
│   │   ├── users/              # Users domain
│   │   │   ├── models.py       # User model (name, study_program, interests)
│   │   │   ├── serializers.py  # User serializers
│   │   │   ├── views.py        # User ViewSet (CRUD operations)
│   │   │   ├── managers.py     # Custom QuerySet methods
│   │   │   ├── urls.py         # URL routing
│   │   │   ├── admin.py        # Admin configuration
│   │   │   └── tests/          # Unit tests
│   │   │
│   │   ├── posts/              # Posts domain
│   │   │   ├── models.py       # Post model (user FK, title, text, image)
│   │   │   ├── serializers.py  # Post serializers
│   │   │   ├── views.py        # Post ViewSet with image upload
│   │   │   ├── managers.py     # Custom QuerySet methods
│   │   │   ├── urls.py         # URL routing
│   │   │   ├── admin.py        # Admin configuration
│   │   │   └── tests/          # Unit tests
│   │   │
│   │   └── comments/           # Comments domain
│   │       ├── models.py       # Comment model (user FK, post FK, text)
│   │       ├── serializers.py  # Comment serializers
│   │       ├── views.py        # Comment ViewSet with filtering
│   │       ├── managers.py     # Custom QuerySet methods
│   │       ├── urls.py         # URL routing
│   │       ├── admin.py        # Admin configuration
│   │       └── tests/          # Unit tests
│   │
│   ├── services/                # Shared services
│   │   └── minio_storage.py    # MinIO storage integration
│   │
│   ├── manage.py               # Django management script
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container config
│   └── entrypoint.sh           # Container startup script
│
├── compose.yaml                # Docker Compose configuration
├── .env                        # Environment variables (create this!)
└── README.md                   # This file
```

### Domain Structure Explanation

Each domain follows a consistent structure:

- **models.py**: Django ORM models with database schema
- **serializers.py**: REST Framework serializers for JSON conversion
- **views.py**: ViewSets for API endpoints (CRUD operations)
- **managers.py**: Custom QuerySet methods for database queries
- **urls.py**: URL routing configuration
- **admin.py**: Django admin panel configuration
- **tests/**: Unit and integration tests

## 🌐 API Endpoints

### Users API (`/api/users/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create a new user |
| GET | `/api/users/{id}/` | Get user details |
| PUT | `/api/users/{id}/` | Update user |
| PATCH | `/api/users/{id}/` | Partial update user |
| DELETE | `/api/users/{id}/` | Delete user |

### Posts API (`/api/posts/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/` | List all posts |
| POST | `/api/posts/` | Create a new post |
| GET | `/api/posts/{id}/` | Get post details |
| PUT | `/api/posts/{id}/` | Update post |
| PATCH | `/api/posts/{id}/` | Partial update post |
| DELETE | `/api/posts/{id}/` | Delete post |
| GET | `/api/posts/my_posts/` | Get current user's posts |

### Comments API (`/api/comments/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comments/` | List all comments |
| POST | `/api/comments/` | Create a new comment |
| GET | `/api/comments/{id}/` | Get comment details |
| PUT | `/api/comments/{id}/` | Update comment |
| PATCH | `/api/comments/{id}/` | Partial update comment |
| DELETE | `/api/comments/{id}/` | Delete comment |
| GET | `/api/comments/by_post/?post_id={id}` | Get comments for a post |
| GET | `/api/comments/by_user/?user_id={id}` | Get comments by a user |

## 🧪 Testing

The project includes automated tests for models, serializers, views, and integration workflows.

### Quick Test Run

```powershell
# From project root
.\run-tests.ps1
```

### Manual Test Run in Docker

```bash
# Start services
docker compose up -d

# Run all tests
docker compose exec backend python -m pytest domains/posts/tests/ -v

# Run specific test file
docker compose exec backend python -m pytest domains/posts/tests/test_models.py -v
```

**Test Coverage:**
- 15 automated tests covering models, serializers, views, and integration
- Tests run in Docker environment with PostgreSQL
- Complete documentation in [be/TESTING.md](be/TESTING.md)
- See [TEST_SUMMARY.md](TEST_SUMMARY.md) for details on what was fixed

## 📮 Testing with Postman

### 1. Create a User

**Request:**
```http
POST http://localhost:8000/api/users/
Content-Type: application/json

{
    "name": "Max Mustermann",
    "study_program": "Computer Science",
    "interests": ["Python", "Django", "Machine Learning", "Web Development"]
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Max Mustermann",
    "study_program": "Computer Science",
    "interests": ["Python", "Django", "Machine Learning", "Web Development"],
    "created_at": "2025-11-24T10:30:00Z"
}
```

### 2. Create a Post (with Text Only)

**Request:**
```http
POST http://localhost:8000/api/posts/
Content-Type: application/json

{
    "user": 1,
    "title": "My First Post",
    "text": "Hello, this is my first post on this platform!"
}
```

**Response:**
```json
{
    "id": 1,
    "user": 1,
    "user_details": {
        "id": 1,
        "name": "Max Mustermann",
        "study_program": "Computer Science",
        "interests": ["Python", "Django", "Machine Learning", "Web Development"],
        "created_at": "2025-11-24T10:30:00Z"
    },
    "title": "My First Post",
    "text": "Hello, this is my first post on this platform!",
    "image": "",
    "created_at": "2025-11-24T10:35:00Z",
    "comment_count": 0
}
```

### 3. Create a Post (with Image)

**Request:**
```http
POST http://localhost:8000/api/posts/
Content-Type: multipart/form-data

Form Data:
- user: 1
- title: "Post with Image"
- text: "Check out this cool image!"
- image_file: [select file from your computer]
```

In Postman:
1. Select `POST` method
2. URL: `http://localhost:8000/api/posts/`
3. Go to **Body** tab
4. Select **form-data**
5. Add fields:
   - `user` (text): `1`
   - `title` (text): `"Post with Image"`
   - `text` (text): `"Check out this cool image!"`
   - `image_file` (file): Select an image file

### 4. Create a Comment

**Request:**
```http
POST http://localhost:8000/api/comments/
Content-Type: application/json

{
    "user": 1,
    "post": 1,
    "text": "Great post! I really enjoyed reading this."
}
```

**Response:**
```json
{
    "id": 1,
    "user": 1,
    "user_details": {
        "id": 1,
        "name": "Max Mustermann",
        "study_program": "Computer Science",
        "interests": ["Python", "Django", "Machine Learning", "Web Development"],
        "created_at": "2025-11-24T10:30:00Z"
    },
    "post": 1,
    "text": "Great post! I really enjoyed reading this.",
    "created_at": "2025-11-24T10:40:00Z"
}
```

### 5. Get All Posts

**Request:**
```http
GET http://localhost:8000/api/posts/
```

### 6. Get Comments for a Specific Post

**Request:**
```http
GET http://localhost:8000/api/comments/by_post/?post_id=1
```

### 7. Search Posts

**Request:**
```http
GET http://localhost:8000/api/posts/?search=first
```

### 8. Update a Post

**Request:**
```http
PATCH http://localhost:8000/api/posts/1/
Content-Type: application/json

{
    "title": "Updated Title"
}
```

### 9. Delete a Post

**Request:**
```http
DELETE http://localhost:8000/api/posts/1/
```

## 🛠️ Development

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database only
docker-compose logs -f db
```

### Running Tests

```bash
docker exec -it social-media-backend python manage.py test
```

### Accessing Django Shell

```bash
docker exec -it social-media-backend python manage.py shell
```

### Stopping Services

```bash
docker-compose down
```

### Stopping and Removing Data

```bash
docker-compose down -v
```

### Rebuilding After Code Changes

```bash
docker-compose up -d --build
```

## 🔍 Common Issues & Solutions

### Issue: Database connection error

**Solution:** Ensure PostgreSQL is running and environment variables are correct:
```bash
docker-compose ps
```

### Issue: MinIO bucket not found

**Solution:** Create the bucket manually:
1. Go to http://localhost:9001
2. Login with `minio` / `minio_admin`
3. Create bucket named `social-media-bucket`

### Issue: Migrations not applied

**Solution:** Run migrations manually:
```bash
docker exec -it social-media-backend python manage.py migrate
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)

## 📄 License

This project is for educational purposes (SWEG course).
