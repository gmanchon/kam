
from kam.app.models.base_database import BaseDatabase


class YamlDatabase(BaseDatabase):

    def __init__(self, params):

        # call base init
        super().__init__(params)
