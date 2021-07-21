
import os

from datetime import datetime

from wagon_common.helpers.git.repo import get_git_top_level_directory


def pluralize(model_name):
    """
    process plural form from singular form
    """

    # TODO: pluralize
    return f"{model_name}s"


def singularize(model_name):
    """
    process singular form from plural form
    """

    # TODO: singularize
    return model_name[:-1]


def get_db_params_path():
    """
    build db params path
    """

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    return os.path.relpath(os.path.join(
        tld,
        "config",
        "database.yml"))


def get_db_migrations_path():
    """
    build db migrations path
    """

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    return os.path.relpath(os.path.join(
        tld,
        "db",
        "migrate"))


def model_code_file(model_name):
    """
    build model code file name from model name
    """

    return f"{model_name.lower()}.py"


def model_code_file_path(model_name):
    """
    build model code file path from model name
    """

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    return os.path.relpath(os.path.join(
        tld,
        "models",
        model_code_file(model_name)))


def model_migration_file(model_name):
    """
    build model migration file name from model name
    """

    # get current date and time
    now = datetime.now()
    timestamp = datetime.strftime(now, "%Y%m%d%H%M%S")

    return f"{timestamp}_create_{model_name.lower()}.py"


def model_migration_file_path(model_name):
    """
    build model migration file path from model name
    """

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    return os.path.relpath(os.path.join(
        tld,
        "db",
        "migrate",
        model_migration_file(model_name)))


def schema_file_path():
    """
    build schema file path
    """

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    return os.path.relpath(os.path.join(
        tld,
        "db",
        "schema.py"))


def model_to_db_table(model_name):
    """
    build db table name from model name
    """

    return pluralize(model_name.lower())
