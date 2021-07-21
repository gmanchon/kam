
from kam.app.models.base_database import BaseDatabase


class ActiveRecordMigration():

    def __init__(self, db_instance: BaseDatabase):
        """
        called when the migration is instantiated
        """

        # store database
        self.db_instance = db_instance

        # call children class change method
        self.change()

    def create_table(self, table_name, columns):
        """
        called by the child class if the migration creates a table
        """

        # create table
        self.db_instance.create_table(table_name, columns)

        # no exception was encountered
        self.migration_successful = True
