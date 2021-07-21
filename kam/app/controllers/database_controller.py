
from kam.app.views.conventions import (
    get_db_params_path,
    get_db_migrations_path)

import yaml


def __load_db_params():
    """
    load db params
    """

    # build db params path
    db_params_path = get_db_params_path()

    # load db conf
    with open(db_params_path, "r") as file:
        db_conf = yaml.safe_load(file)

    # build migrations path
    migrations_path = get_db_migrations_path()

    return db_conf, migrations_path


def migrate():
    """
    migrate database
    """

    # load db params
    db_params, migrations_path = __load_db_params()

    print(db_params, migrations_path)

    print("migrate")
    pass
