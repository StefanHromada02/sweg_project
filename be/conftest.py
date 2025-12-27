"""
Pytest configuration for Django tests.
"""
import pytest
import os
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """Override database setup to use SQLite in-memory for tests."""
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }


# pytest-django automatically handles Django setup
# No additional configuration needed - tests run in Docker with PostgreSQL
