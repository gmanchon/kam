
from kam.app.controllers.database_controller import instantiate_db

from kam.app.views.conventions import model_to_db_table


class ActiveRecord():

    # retrieve db connection
    db = instantiate_db()

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

        # remove id from columns
        cols = {k: v for k, v in self.__dict__.items() if k != "id"}

        # check whether object was persisted
        if self.id is None:

            # insert object
            self.db.insert(table_name, self, cols)

        else:

            # update object
            self.db.update(table_name, self.id, cols)
