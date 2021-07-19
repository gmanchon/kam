
from kam.app.models.yaml_database import YamlDatabase
from kam.app.models.sql_database import SqlDatabase

from kam.app.views.conventions import (
    get_db_params_path,
    get_db_migrations_path)

import os
import glob
import yaml


def __load_param(db_params_path, conf, key):
    """
    load conf param
    """

    # retrieve param
    value = conf.get(key)

    # validate param
    if value is None:
        raise ValueError(f"Invalid parameters in {db_params_path}: missing {key} key 🤒")

    return value


def __load_db_params():
    """
    load db params
    """

    # build db params path
    db_params_path = get_db_params_path()

    # load db conf
    with open(db_params_path, "r") as file:
        db_conf = yaml.safe_load(file)

    # retrieve db params
    db_parameters = __load_param(db_params_path, db_conf, "database")
    db_type = __load_param(db_params_path, db_parameters, "type")
    db_params = __load_param(db_params_path, db_parameters, "params")

    return db_type, db_params


def instantiate_db():
    """
    return application db instance
    """

    # load db params
    db_type, db_params = __load_db_params()

    # instanciate database
    if db_type == "yaml":
        db_instance = YamlDatabase(db_params)
    elif db_type == "sql":
        db_instance = SqlDatabase(db_params)

    return db_instance


def retrieve_code_migrations():
    """
    retrieve migrations list
    """

    # build migrations path
    migrations_path = get_db_migrations_path()

    # build migrations pattern
    migrations_pattern = os.path.join(
        migrations_path,
        "*")

    # list migrations
    migration_files = glob.glob(migrations_pattern)

    return migration_files


def migration_klass_name_from_filename(migration_path):
    """
    process migration klass name from filename
    """

    # process basename
    migration_basename = os.path.basename(migration_path)

    # process raw filename (remove extension)
    migration_raw_filename = os.path.splitext(migration_basename)[0]

    # remove timestamp
    migration_content = migration_raw_filename.split("_")[1:]

    # process klass name
    migration_klass_name = "".join([w.capitalize() for w in migration_content])

    return migration_klass_name


def run_migration(migration_path):
    """
    run migration
    """

    # build migration klass name
    migration_klass_name = migration_klass_name_from_filename(migration_path)
    print(migration_klass_name)

    # load class
    # from https://stackoverflow.com/questions/4821104/dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported-module


def migrate():
    """
    migrate database
    """

    # create db instance
    db_instance = instantiate_db()

    # retrieve current migration
    db_migrations = db_instance.migrations()

    # retrieve migrations
    code_migrations = sorted(retrieve_code_migrations())

    # process max executed migration
    max_migration = max(db_migrations)

    # iterate through code migrations
    required_migrations = [m for m in code_migrations if os.path.basename(m).split("_")[0] > max_migration]

    # process migrations
    for migration in required_migrations:

        # run migration
        run_migration(migration)
