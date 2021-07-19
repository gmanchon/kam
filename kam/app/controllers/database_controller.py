
from kam.app.views.conventions import (
    get_db_params_path,
    get_db_migrations_path)

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

    # build migrations path
    migrations_path = get_db_migrations_path()

    return db_type, db_params, migrations_path


def migrate():
    """
    migrate database
    """

    # load db params
    db_type, db_params, migrations_path = __load_db_params()

    print(db_type, db_params, migrations_path)

    print("migrate")
    pass
