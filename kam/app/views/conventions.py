
import re
import os
import yaml

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


def get_app_directory_path():
    """
    return app directory
    """

    # retrieve app params
    app_params_path = get_app_params_path()

    # load app conf
    app_conf = {}

    if os.path.isfile(app_params_path):
        with open(app_params_path, "r") as file:
            app_conf = yaml.safe_load(file)

    # retrieve app directory
    app_directory = app_conf.get("app_directory", "app")

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    # build app path
    app_directory_path = os.path.relpath(
        os.path.join(
            tld,
            app_directory))

    return app_directory_path


def get_app_params_path():
    """
    build app params path
    """

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    return os.path.relpath(os.path.join(
        tld,
        "kam.yml"))


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


def model_code_file_path(model_klass_name):
    """
    build model code file path from model name
    """

    # build db table name
    db_table_name = model_to_db_table(model_klass_name)

    # retrieve app directory path
    app_path = get_app_directory_path()

    return os.path.relpath(os.path.join(
        app_path,
        "models",
        model_code_file(singularize(db_table_name))))


def model_migration_file(model_klass_name):
    """
    build model migration file name from model name
    """

    # build db table name
    db_table_name = model_to_db_table(model_klass_name)

    # get current date and time
    now = datetime.now()
    timestamp = datetime.strftime(now, "%Y%m%d%H%M%S")

    return f"{timestamp}_create_{db_table_name}.py"


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


def model_to_db_table(model_klass_name):
    """
    build db table name from model klass name
    """

    # split title words
    split_name = "_".join(re.findall('[A-Z][^A-Z]*', model_klass_name))

    return pluralize(split_name.lower())


def model_to_db_table_ref(model_klass_name):
    """
    build db table fk id from model klass name
    """

    # split title words
    return singularize(model_to_db_table(model_klass_name))


def model_to_db_table_fk_id(model_klass_name):
    """
    build db table fk id from model klass name
    """

    # split title words
    return f"{model_to_db_table_ref(model_klass_name)}_id"


def model_name_to_klass_name(model_name):
    """
    build klass name from model name
    """

    return "".join([w.capitalize() for w in model_name.split("_")])
