
from kam.app.models.base_database import BaseDatabase

import uuid

import psycopg2


class SqlDatabase(BaseDatabase):

    def __init__(self, params):

        # retrieve params
        self.params = params
        self.connection_params = params.get("connection", {})

        # create database connection
        self.conn = psycopg2.connect(**self.connection_params)

        # call base init
        super().__init__(params)

    def migrations_table_exists(self):

        # query
        check_migrations_table = """
        SELECT * FROM pg_catalog.pg_tables WHERE tablename = 'schema_migrations';
        """

        # retrieve content of migrations table
        cur = self.conn.cursor()
        cur.execute(check_migrations_table)
        tables = cur.fetchall()

        # check whether migration table exists
        if len(tables) == 0:
            return False

        return True

    def create_migrations_table(self):

        # query
        create_migrations_table = """
        CREATE TABLE schema_migrations (
          version TEXT
        );
        """

        # create migrations table
        cur = self.conn.cursor()
        cur.execute(create_migrations_table)

        # commit
        self.conn.commit()

    def retrieve_migrations(self):

        # query
        get_migrations = """
        SELECT version FROM schema_migrations;
        """

        # retrieve migrations
        cur = self.conn.cursor()
        cur.execute(get_migrations)
        migrations = cur.fetchall()

        return [m[0] for m in migrations]

    def migrations(self):

        # check migrations table existence
        if not self.migrations_table_exists():

            print("create migrations table")
            self.create_migrations_table()

        # retrieve migrations
        migrations = self.retrieve_migrations()

        return migrations

    def create_table(self, table_name, columns):
        """
        called by active record migration
        """

        # build column list
        column_list = {k: v for k, v in columns.items() if k != "timestamps"}

        # retrieve timestamps
        timestamps = columns.get("timestamps", True)

        # query
        statements = [
            f"CREATE TABLE {table_name} (",
            "id BIGSERIAL NOT NULL"]

        # add columns
        for column, data_type in column_list.items():

            if data_type == "string":
                statements.append(f"{column} VARCHAR NULL")
            elif data_type == "integer":
                statements.append(f"{column} INT64 NULL")
            elif data_type == "references":
                statements.append(f"{column} BIGSERIAL NOT NULL")

        # add timestamps
        if timestamps:

            statements.append("created_at TIMESTAMP NOT NULL")
            statements.append("updated_at TIMESTAMP NOT NULL")

        # add constraints
        statements.append(f"CONSTRAINT {table_name}_pkey PRIMARY KEY (id)")

        # add foreign keys
        for column, data_type in column_list.items():

            if data_type == "references":

                # generate fk unique id
                unique_fk_id = uuid.uuid4().hex

                statements.append(
                    f"CONSTRAINT fk_kam_{unique_fk_id} "
                    + f"FOREIGN KEY ({column}_id) "
                    + f"REFERENCES public.{column}(id)")

        # add table end
        statements.append(");")

        # close lines with commas
        create_migrations_table = (
            statements[0]
            + "\n"
            + ",\n".join(statements[1:-1])
            + statements[-1])

        print(create_migrations_table)
        exit()

        # create migrations table
        cur = self.conn.cursor()
        cur.execute(create_migrations_table)  # create table does not seem to support prepared statements

        # commit
        self.conn.commit()
