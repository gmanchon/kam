
from kam.app.controllers.database_controller import instantiate_db
from kam.app.models.active_record_schema import ActiveRecordSchema

from kam.app.views.conventions import (
    model_to_db_table,
    schema_file_path)

import os

import importlib


class ActiveRecord():

    # retrieve db connection
    db = instantiate_db()

    def __load_db_schema():
        """
        load schema into class variable
        """

        # TODO: kampai to determine project path
        # build seed location
        schema_path = schema_file_path()

        # build module name
        module_name = schema_path.replace(os.sep, '.')

        # load script
        # from https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
        spec = importlib.util.spec_from_file_location(module_name, schema_path)
        module = importlib.util.module_from_spec(spec)

        # run the seed
        spec.loader.exec_module(module)

    # db schema
    db_schema = __load_db_schema()

    del __load_db_schema  # delete tmp function

    def __init__(self):

        # retrieve db connection
        self.db = instantiate_db()

    @classmethod
    def destroy_all(cls):
        """
        delete all rows
        """

        # get child class name
        child_klass_name = cls.__name__
        table_name = model_to_db_table(child_klass_name)

        print(f"\ndestroy all {table_name}...")

        cls.db.destroy_all(table_name)

    def save(self):
        """
        insert or update row
        """

        # get child class name
        child_klass_name = type(self).__name__
        table_name = model_to_db_table(child_klass_name)

        # retrieve table schema
        table_schema = ActiveRecordSchema.db_schema[table_name]

        # remove id from columns
        cols = {k: v for k, v in self.__dict__.items() if k != "id"}

        # replace references
        valid_cols = {}

        for column, value in cols.items():

            # checking whether value is an active record object (a reference)
            if issubclass(type(value), ActiveRecord):

                # replace the reference by its id
                column = f"{column}_id"
                value = value.id

            # append value
            valid_cols[column] = value

        # check whether object was persisted
        if self.id is None:

            # insert object
            self.db.insert(table_name, table_schema, self, valid_cols)

        else:

            # update object
            self.db.update(table_name, table_schema, self.id, valid_cols)
