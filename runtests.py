#!/usr/bin/env python3
"""Utility script to setup Django and run tests against package"""
import sys
from os.path import dirname, join

try:
    from django import setup
    from django.apps import apps
    from django.conf import settings
    from django.core.management import execute_from_command_line
except ImportError:
    print(
        "Could not load Django.\n"
        "Try running `flit install --symlink` before `./runtests.py`\n"
        "or run `make test` (or `make tox`) for an all in one solution",
    )
    exit(-1)


try:
    import improved_user  # noqa: F401 pylint: disable=unused-import
except ImportError:
    print(
        "Could not load improved_user!\n"
        "Try running `flit install --symlink` before `./runtests.py`\n"
        "or run `make test` (or `make tox`) for an all in one solution",
    )
    exit(-1)


def configure_django():
    """Configure Django before tests"""
    settings.configure(
        SECRET_KEY="m-4Umd2!_nQQX.Ux6dYaiffmgRFpFxri!hqmffqBAhuAu*-!9n",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            },
        },
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.sessions",
            "django.contrib.sites",
            "improved_user.apps.ImprovedUserConfig",
        ],
        SITE_ID=1,
        AUTH_USER_MODEL="improved_user.User",
        FIXTURE_DIRS=(join(dirname(__file__), "tests", "fixtures"),),
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                        "django.template.context_processors.request",
                    ],
                },
            }
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
    )
    setup()


def run_test_suite(*args):
    """Run the test suite"""
    test_args = list(args) or []
    execute_from_command_line(["manage.py", "test"] + test_args)


def check_missing_migrations():
    """Check that user model and migration files are in sync"""
    from django.db.migrations.autodetector import MigrationAutodetector
    from django.db.migrations.loader import MigrationLoader
    from django.db.migrations.questioner import (
        NonInteractiveMigrationQuestioner as Questioner,
    )
    from django.db.migrations.state import ProjectState

    loader = MigrationLoader(None, ignore_no_migrations=True)
    conflicts = loader.detect_conflicts()
    if conflicts:
        raise Exception(
            "Migration conflicts detected. Please fix your migrations."
        )
    questioner = Questioner(dry_run=True, specified_apps=None)
    autodetector = MigrationAutodetector(
        loader.project_state(),
        ProjectState.from_apps(apps),
        questioner,
    )
    changes = autodetector.changes(
        graph=loader.graph,
        trim_to_apps=None,
        convert_apps=None,
        migration_name=None,
    )
    if changes:
        raise Exception(
            "Migration changes detected. "
            "Please update or add to the migration file as appropriate"
        )
    print("Migration-checker detected no problems.")


if __name__ == "__main__":
    configure_django()
    check_missing_migrations()
    run_test_suite(*sys.argv[1:])
