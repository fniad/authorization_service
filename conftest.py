import pytest
from django.core.management import call_command


@pytest.fixture(autouse=True, scope="session")
def prepare_test_database(django_db_blocker):
    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0)

@pytest.fixture(scope='session', autouse=True)
def enable_db_access_for_session_fixture(django_db_setup, django_db_blocker):
    pass  # Пустая фикстура для разрешения доступа к базе данных во время сессии
