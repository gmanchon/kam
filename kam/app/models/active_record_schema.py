
class ActiveRecordSchema():

    # database schema
    db_schema = {}

    @classmethod
    def define(cls, definition_function):

        # instantiate ar schema
        ar_schema = ActiveRecordSchema()

        # call definition function
        definition_function(ar_schema)

    def create_table(self, table_name, columns, constraints):
        """
        called by the schema when loaded
        """

        # fill db schema
        self.db_schema[table_name] = dict(
            columns=columns,
            constraints=constraints)
