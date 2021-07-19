
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


def migrate():
    """
    migrate database
    """

    # create db instance
    db_instance = instantiate_db()

    # retrieve current migration
    db_migrations = db_instance.migrations()

    print(db_migrations)

    # retrieve migrations
    migrations = retrieve_code_migrations()

    print(migrations)
