"""
Pytest configuration for Django tests.
"""
import pytest
import os
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    """Override database setup to use SQLite in-memory for tests."""
    from django.core.management import call_command
    
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    
    with django_db_blocker.unblock():
        # Create tables using Django migrations
        call_command('migrate', '--run-syncdb', verbosity=0)


# pytest-django automatically handles Django setup
# No additional configuration needed - tests run in Docker with PostgreSQL
