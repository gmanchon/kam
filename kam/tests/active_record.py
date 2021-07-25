
# TODO: this is a wip

from kam.app.controllers.model_controller import create
from kam.app.controllers.database_controller import (
    create_database,
    drop_database,
    migrate,
    seed)


def test_where():

    create(model_klass_name, instance_variables)

    create_database()
    migrate()
    seed()
    drop_database()
