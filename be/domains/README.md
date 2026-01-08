# Django Domains - Struktur und Erklärung

Dieses Dokument erklärt die Domain-Driven Design (DDD) Struktur unseres Django-Projekts und was Django mit den verschiedenen Dateien macht.

## 📁 Was ist eine Domain?

Eine **Domain** ist ein eigenständiger Bereich der Anwendung, der eine spezifische Geschäftslogik kapselt. In unserem Projekt haben wir drei Domains:
- `users` - Benutzerverwaltung
- `posts` - Blog-Posts mit Bildern
- `comments` - Kommentare zu Posts

Jede Domain ist eine vollständige **Django App** mit eigener Datenbank, API und Logik.

---

## 📄 Dateien in einer Domain und ihre Funktion

### `__init__.py`
**Was steht drin:**
```python
default_app_config = 'domains.users.apps.UsersConfig'
```

**Was Django damit macht:**
- Django erkennt dieses Verzeichnis als Python-Package
- Die Zeile `default_app_config` sagt Django, welche App-Konfiguration geladen werden soll
- Diese Zeile ist optional in neueren Django-Versionen, aber empfohlen für Klarheit

---

### `apps.py`
**Was steht drin:**
```python
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.users'
```

**Was Django damit macht:**
- **AppConfig** ist die zentrale Konfigurationsklasse für eine Django-App
- `default_auto_field`: Definiert den Typ für automatische Primary Keys (ID-Felder)
- `name`: Der vollständige Python-Pfad zur App (wichtig für Django's App-Registry)
- Django lädt diese Konfiguration beim Start und registriert die App intern

**Wann Django das nutzt:**
- Beim Server-Start
- Bei `python manage.py migrate`
- Bei `python manage.py makemigrations`
- In der Admin-Oberfläche

---

### `models.py`
**Was steht drin:**
```python
from django.db import models
from .managers import UserManager

class User(models.Model):
    name = models.CharField(max_length=200)
    study_program = models.CharField(max_length=200)
    interests = ArrayField(models.CharField(max_length=100), size=5)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
```

**Was Django damit macht:**
- **Jede Klasse = Eine Datenbank-Tabelle**
- `models.Model`: Basisklasse, die Django sagt "Das ist eine Datenbank-Entität"
- **Feldtypen** (CharField, DateTimeField, etc.):
  - Django generiert daraus SQL CREATE TABLE Statements
  - Validiert Daten beim Speichern
  - Konvertiert Python-Typen ↔ Datenbank-Typen

**Beispiel-SQL das Django generiert:**
```sql
CREATE TABLE "users_user" (
    "id" bigserial PRIMARY KEY,
    "name" varchar(200) NOT NULL,
    "study_program" varchar(200) NOT NULL,
    "interests" varchar(100)[5],
    "created_at" timestamp with time zone NOT NULL
);
```

**Field-Parameter:**
- `max_length=200`: Maximale Zeichenlänge
- `auto_now_add=True`: Django setzt automatisch aktuelles Datum beim Erstellen
- `on_delete=models.CASCADE`: Wenn referenziertes Objekt gelöscht wird, lösche auch dieses

**ForeignKey-Beispiel (Comment → User):**
```python
user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')
```
- Erstellt eine Fremdschlüssel-Beziehung in der Datenbank
- `related_name='comments'`: Ermöglicht Zugriff von User zu Comments: `user.comments.all()`

---

### `managers.py`
**Was steht drin:**
```python
from django.db import models

class UserQuerySet(models.QuerySet):
    def by_study_program(self, program):
        return self.filter(study_program__iexact=program)

class UserManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    def by_study_program(self, program):
        return self.get_queryset().by_study_program(program)
```

**Was Django damit macht:**
- **Manager** (`objects`): Der Einstiegspunkt für alle Datenbank-Queries
  - `User.objects.all()` ← `objects` ist der Manager
  - Der Manager erstellt QuerySets
  
- **QuerySet**: Ein "lazy" Datenbank-Query-Objekt
  - Queries werden erst ausgeführt, wenn Daten wirklich gebraucht werden
  - Kann gekettet werden: `User.objects.filter(...).order_by(...).first()`

**Wie Django das nutzt:**
```python
# Django erstellt intern:
SELECT * FROM users_user WHERE study_program ILIKE 'Computer Science'

# Wenn man aufruft:
User.objects.by_study_program("Computer Science")
```

**QuerySet-Methoden die Django kennt:**
- `.filter()` → WHERE clause
- `.exclude()` → WHERE NOT clause
- `.order_by()` → ORDER BY clause
- `.select_related()` → JOIN (ForeignKey vorladen)
- `.prefetch_related()` → Mehrere Queries optimiert (Many-to-Many)

---

### `serializers.py`
**Was steht drin:**
```python
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "study_program", "interests", "created_at"]
        read_only_fields = ["created_at"]
```

**Was Django REST Framework (DRF) damit macht:**
- **Serializer**: Konvertiert zwischen Python-Objekten und JSON
  
**Zwei Richtungen:**
1. **Serialization** (Model → JSON):
   ```python
   user = User.objects.first()
   serializer = UserSerializer(user)
   return Response(serializer.data)  # → JSON für API-Response
   ```

2. **Deserialization** (JSON → Model):
   ```python
   serializer = UserSerializer(data=request.data)
   if serializer.is_valid():
       serializer.save()  # → Speichert in Datenbank
   ```

**Was passiert intern:**
- DRF liest `Meta.model` und `Meta.fields`
- Erstellt automatisch Validierungsregeln basierend auf Model-Feldern
- `read_only_fields`: Diese Felder werden nur ausgegeben, nie als Input akzeptiert

**Validierung:**
```python
def validate_interests(self, value):
    if len(value) > 5:
        raise serializers.ValidationError("Max 5 interests")
    return value
```
- DRF ruft diese Methode automatisch auf bei `is_valid()`
- Naming-Convention: `validate_<feldname>`

---

### `views.py`
**Was steht drin:**
```python
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

**Was Django REST Framework damit macht:**
- **ViewSet**: Kombiniert mehrere Views in einer Klasse
- **ModelViewSet**: Bietet automatisch alle CRUD-Operationen

**Django erstellt automatisch diese Endpoints:**
- `GET /api/users/` → `list()` → Alle User
- `POST /api/users/` → `create()` → Neuen User erstellen
- `GET /api/users/1/` → `retrieve()` → User mit ID 1
- `PUT /api/users/1/` → `update()` → User komplett aktualisieren
- `PATCH /api/users/1/` → `partial_update()` → User teilweise aktualisieren
- `DELETE /api/users/1/` → `destroy()` → User löschen

**Request-Flow:**
```
1. HTTP Request kommt an
   ↓
2. Django Router findet passende URL
   ↓
3. ViewSet-Methode wird aufgerufen (z.B. create)
   ↓
4. Serializer validiert Daten
   ↓
5. Model wird gespeichert
   ↓
6. Serializer erstellt JSON-Response
   ↓
7. HTTP Response wird gesendet
```

**Custom Actions:**
```python
@action(detail=False, methods=['get'])
def by_post(self, request):
    post_id = request.query_params.get('post_id')
    comments = Comment.objects.filter(post_id=post_id)
    serializer = self.get_serializer(comments, many=True)
    return Response(serializer.data)
```
- `@action`: Erstellt custom Endpoint
- `detail=False`: Endpoint ohne ID → `/api/comments/by_post/`
- `detail=True`: Endpoint mit ID → `/api/comments/1/custom_action/`

---

### `urls.py`
**Was steht drin:**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
```

**Was Django damit macht:**
- **Router**: Erstellt automatisch URL-Patterns für ViewSets
- `router.register(r"", UserViewSet)`: Registriert alle ViewSet-Actions

**Django generiert diese URLs:**
```
/                    → GET:  list,    POST: create
/<pk>/               → GET:  retrieve, PUT: update, PATCH: partial_update, DELETE: destroy
/by_post/            → GET:  custom action (wenn @action decorator genutzt)
```

**URL-Hierarchie:**
```
config/urls.py:
    path("api/users/", include("domains.users.urls"))
    ↓
domains/users/urls.py:
    path("", include(router.urls))
    ↓
Finale URLs:
    /api/users/
    /api/users/1/
    /api/users/by_study_program/
```

---

### `admin.py`
**Was steht drin:**
```python
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'study_program', 'created_at')
    search_fields = ('name', 'study_program')
    readonly_fields = ('created_at',)
```

**Was Django damit macht:**
- **Django Admin**: Automatisch generierte Verwaltungs-Oberfläche
- `@admin.register(User)`: Registriert Model im Admin
- Django erstellt automatisch:
  - Liste aller Objekte
  - Detailansicht zum Bearbeiten
  - Suchfunktion
  - Filter

**Admin-Konfiguration:**
- `list_display`: Welche Felder in der Tabellen-Übersicht
- `search_fields`: In welchen Feldern gesucht werden kann
- `readonly_fields`: Felder die nicht editiert werden können
- `list_filter`: Sidebar-Filter

**Zugriff:** `http://localhost:8000/admin/`

---

### `migrations/`
**Was steht drin:**
```python
# migrations/0001_initial.py
class Migration(migrations.Migration):
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ...
            ],
        ),
    ]
```

**Was Django damit macht:**
- **Migrationen**: Versions-Kontrolle für Datenbank-Schema
- Django vergleicht Models mit Datenbank
- Erstellt Python-Code der Schema-Änderungen beschreibt

**Befehle:**
```bash
# Django analysiert models.py und erstellt Migration-Dateien
python manage.py makemigrations

# Django führt SQL-Befehle aus, um Datenbank zu ändern
python manage.py migrate
```

**Migration-Chain:**
```
0001_initial.py (Tabelle erstellen)
  ↓
0002_add_email_field.py (Feld hinzufügen)
  ↓
0003_alter_name_max_length.py (Feld ändern)
```

**Dependencies:**
```python
dependencies = [
    ('users', '0001_initial'),  # Diese Migration muss zuerst laufen
]
```
- Django stellt sicher, dass Migrationen in der richtigen Reihenfolge laufen
- Wichtig bei ForeignKeys zwischen Domains

---

### `tests/`
**Was steht drin:**
```python
from django.test import TestCase
from .models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(name="Test", study_program="CS")
        self.assertEqual(user.name, "Test")
```

**Was Django damit macht:**
- Django erstellt temporäre Test-Datenbank
- Führt Tests aus
- Löscht Test-Datenbank wieder

**Test-Flow:**
```
1. Django erstellt Test-DB
2. Führt setUp() aus
3. Führt test_*() Methoden aus
4. Führt tearDown() aus
5. Löscht Test-DB
```

**Befehl:** `python manage.py test`

---

## 🔄 Zusammenspiel der Dateien - Kompletter Request-Flow

### Beispiel: `POST /api/users/` mit `{"name": "Max", "study_program": "CS"}`

```
1. Django empfängt Request
   ↓
2. urls.py: Django findet Route "api/users/" → users.urls
   ↓
3. users/urls.py: Router leitet zu UserViewSet.create()
   ↓
4. views.py: ViewSet erhält Request-Daten
   ↓
5. serializers.py: UserSerializer validiert Daten
   - Prüft ob alle Required Fields da sind
   - Ruft validate_interests() auf
   ↓
6. models.py: User-Objekt wird erstellt
   - Manager: User.objects.create()
   - Django generiert: INSERT INTO users_user ...
   ↓
7. serializers.py: UserSerializer konvertiert zu JSON
   ↓
8. views.py: Response mit Status 201 Created
   ↓
9. Django sendet HTTP Response
```

---

## 🎯 Warum diese Struktur?

### Separation of Concerns
- **models.py**: Was gespeichert wird (Datenstruktur)
- **serializers.py**: Wie Daten validiert/konvertiert werden
- **views.py**: Was bei Requests passiert (Business Logic)
- **urls.py**: Welche Endpoints existieren (Routing)
- **managers.py**: Wie Daten abgefragt werden (Query Logic)

### Vorteile
- **Wiederverwendbar**: Serializer kann in mehreren Views genutzt werden
- **Testbar**: Jede Komponente kann isoliert getestet werden
- **Wartbar**: Änderungen an einer Stelle betreffen nicht alles andere
- **Django-konform**: Folgt Django Best Practices

---

## 📚 Django's Magie - Was automatisch passiert

### 1. **ORM (Object-Relational Mapping)**
```python
# Du schreibst:
User.objects.filter(study_program="CS")

# Django macht daraus:
SELECT * FROM users_user WHERE study_program = 'CS'
```

### 2. **Automatic Admin**
- Django erstellt komplette Verwaltungs-UI nur durch `@admin.register()`

### 3. **Migrations**
- Django trackt alle Model-Änderungen automatisch

### 4. **Validation**
- Model-Constraints → Automatische Validierung
- Serializer → Automatische Input-Validierung

### 5. **REST Framework Auto-API**
- ModelViewSet → Komplette CRUD-API ohne Code

---

## 🚀 Nützliche Django-Befehle

```bash
# App erstellen
python manage.py startapp domain_name

# Migrationen erstellen
python manage.py makemigrations

# Migrationen anwenden
python manage.py migrate

# Admin-User erstellen
python manage.py createsuperuser

# Django Shell (zum Testen)
python manage.py shell
>>> from domains.users.models import User
>>> User.objects.all()

# Server starten
python manage.py runserver
```

---

## 📖 Weiterführende Konzepte

### Lazy Evaluation (QuerySets)
```python
# Diese Zeile macht KEINEN Datenbank-Query:
users = User.objects.filter(study_program="CS")

# Erst hier wird Query ausgeführt:
for user in users:  # Iteration triggert Query
    print(user.name)
```

### Select Related vs Prefetch Related
```python
# Select Related (ForeignKey): 1 Query mit JOIN
posts = Post.objects.select_related('user').all()

# Prefetch Related (Many-to-Many): 2 separate Queries
posts = Post.objects.prefetch_related('comments').all()
```

### Signals
```python
# Automatisch ausgeführt nach Model-Save
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        print(f"New user: {instance.name}")
```

---

**Erstellt für SWEG Project - Django Backend**
