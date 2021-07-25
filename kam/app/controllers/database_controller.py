
from kam.app.models.yaml_database import YamlDatabase
from kam.app.models.sql_database import SqlDatabase

from kam.app.helpers.file import (
    get_db_params_path,
    get_db_migrations_path)

from wagon_common.helpers.git.repo import get_git_top_level_directory

import os
import glob
import yaml

import importlib


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


def instantiate_db(no_schema=False):
    """
    return application db instance
    """

    # load db params
    db_type, db_params = __load_db_params()

    # instanciate database
    if db_type == "yaml":
        db_instance = YamlDatabase(db_params)
    elif db_type == "sql":
        db_instance = SqlDatabase(db_params, no_schema=no_schema)

    return db_instance


def drop_database():
    """
    drop database, no confirmations
    """

    # create db instance
    db_instance = instantiate_db(no_schema=True)

    # drop database
    db_instance.drop_database()


def create_database():
    """
    create database
    """

    # create db instance
    db_instance = instantiate_db(no_schema=True)

    # create database
    db_instance.create_database()

    # init db instance
    init_db_instance = instantiate_db()

    # init database
    init_db_instance.initialize_database()


def dump_schema():
    """
    dump database schema in db/schema.py
    """

    # create db instance
    db_instance = instantiate_db()

    # create database
    db_instance.dump_schema()


def retrieve_code_migrations():
    """
    retrieve migrations list
    """

    # build migrations path
    migrations_path = get_db_migrations_path()

    # build migrations pattern
    migrations_pattern = os.path.join(
        migrations_path,
        "*.py")

    # list migrations
    migration_files = glob.glob(migrations_pattern)

    return migration_files


def migration_timestamp(migration_path):
    """
    retrieve migration timestamp from migration path
    """

    # build migration timestamp
    migration_timestamp = os.path.basename(migration_path).split("_")[0]

    return migration_timestamp


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


def process_module_path(migration_path):
    """
    process module path
    """

    # process module and submodules
    return os.path.splitext(migration_path)[0].replace(os.sep, ".")


def run_migration(db_instance, migration_path):
    """
    run migration
    """

    # build migration klass name
    migration_klass = migration_klass_name_from_filename(migration_path)

    # process module and submodules
    module_path = process_module_path(migration_path)

    # load class
    # from https://stackoverflow.com/questions/4821104/dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported-module
    MigrationKlass = getattr(importlib.import_module(module_path), migration_klass)

    # instantitate class
    migration_instance = MigrationKlass(db_instance)

    # return migration status
    return migration_instance.migration_successful


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
    max_migration = max(db_migrations) if len(db_migrations) > 0 else "0"

    # iterate through code migrations
    required_migrations = [m for m in code_migrations if migration_timestamp(m) > max_migration]

    # process migrations
    migration_count = len(required_migrations)

    for index, migration in enumerate(required_migrations):

        print(f"\nrun migration {migration} ({index + 1}/{migration_count})")

        # run migration
        migration_successful = run_migration(db_instance, migration)

        # update migration table
        if not migration_successful:

            # stop migrations
            break

        # mark migration as done
        db_instance.mark_migration_done(migration_timestamp(migration))

    # update db schema
    dump_schema()


def seed():
    """
    seed the database
    """

    # retrieve project top level directory
    tld = get_git_top_level_directory()

    # build seed location
    seed_path = os.path.relpath(os.path.join(
        tld,
        "db",
        "seed.py"))

    # build module name
    module_name = seed_path.replace(os.sep, '.')

    # load script
    # from https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    spec = importlib.util.spec_from_file_location(module_name, seed_path)
    module = importlib.util.module_from_spec(spec)

    # run the seed
    spec.loader.exec_module(module)
