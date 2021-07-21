
class ActiveRecordSchema():

    @classmethod
    def define(cls, definition_function):

        # create schema definition
        schema_definition = {}

        # call definition function
        definition_function(schema_definition)

        print(schema_definition)

        return schema_definition

    def create_table(self, table_name, columns):
        """
        called by the schema when loaded
        """

        # TODO: store table and columns
        print("ACTIVE RECORD SCHEMA create_table called 🔥")
