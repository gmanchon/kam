
from kam.app.models.base_database import BaseDatabase

from kam.app.views.conventions import pluralize

import uuid

import psycopg2


class SqlDatabase(BaseDatabase):

    def __init__(self, params, no_schema=False):

        # retrieve params
        self.params = params
        self.connection_params = params.get("connection", {})

        # retrieve db name and user
        self.host = self.connection_params.get("host")
        self.port = self.connection_params.get("port")
        self.dbname = self.connection_params.get("dbname")
        self.user = self.connection_params.get("user")
        self.password = self.connection_params.get("password")

        # create database connection
        if not no_schema:

            # connect to schema
            self.conn = psycopg2.connect(**self.connection_params)

        else:

            # connect without specifying the database schema (create and drop db)
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname="postgres",
                user=self.user,
                password=self.password)

        # call base init
        super().__init__(params)

    def drop_database(self):
        """
        drop database
        """

        # query
        drop_database_query = f"DROP DATABASE IF EXISTS {self.dbname};"

        print()
        print(drop_database_query)

        # cannot drop inside of a transaction
        self.conn.autocommit = True

        # drop database
        cur = self.conn.cursor()
        cur.execute(drop_database_query)

        # reset autocommit
        self.conn.autocommit = False

    def create_database(self):
        """
        create database
        """

        # query
        create_database_query = f"CREATE DATABASE {self.dbname}" \
            + f"\nWITH OWNER = {self.user};"

        print()
        print(create_database_query)

        # cannot drop inside of a transaction
        self.conn.autocommit = True

        # drop database
        cur = self.conn.cursor()
        cur.execute(create_database_query)

        # reset autocommit
        self.conn.autocommit = False

    def initialize_database(self):
        """
        initialize database
        """

        # create timestamps trigger
        self.create_database_timestamps_trigger_function()

    def create_database_timestamps_trigger_function(self):
        """
        create timestamps trigger
        """

        # query
        db_timestamps_trigger = (
            "CREATE OR REPLACE FUNCTION trigger_set_timestamp()"
            + "\nRETURNS TRIGGER AS $$"
            + "\nBEGIN"
            + "\n  NEW.updated_at = NOW();"
            + "\n  RETURN NEW;"
            + "\nEND;"
            + "\n$$ LANGUAGE plpgsql;")

        print()
        print(db_timestamps_trigger)

        # create trigger
        cur = self.conn.cursor()
        cur.execute(db_timestamps_trigger)

        # commit
        self.conn.commit()

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

    def mark_migration_done(self, migration):

        # TODO: use postgres prepared statements

        # query
        set_migration_done = f"""
        INSERT INTO schema_migrations (version) values({migration});
        """

        # retrieve migrations
        cur = self.conn.cursor()
        cur.execute(set_migration_done)

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

            print("\ncreate migrations table")
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
            f"CREATE TABLE \"{table_name}\" (",
            "id BIGSERIAL NOT NULL"]

        # add columns
        for column, data_type in column_list.items():

            if data_type == "string":
                statements.append(f"\"{column}\" VARCHAR NULL")
            elif data_type == "integer":
                statements.append(f"\"{column}\" INT64 NULL")
            elif data_type == "references":
                statements.append(f"{column}_id BIGSERIAL NOT NULL")

        # add timestamps
        if timestamps:

            statements.append("created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
            statements.append("updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")

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
                    + f"REFERENCES public.{pluralize(column)}(id)")

        # add table end
        statements.append(");")

        # close lines with commas
        create_table = (
            statements[0]
            + "\n"
            + ",\n".join(statements[1:-1])
            + statements[-1])

        print()
        print(create_table)

        # create migrations table
        cur = self.conn.cursor()
        cur.execute(create_table)  # create table does not seem to support prepared statements

        # commit
        self.conn.commit()

        # create table timestamps trigger
        if timestamps:

            self.add_table_timestamps_trigger(table_name)

    def add_table_timestamps_trigger(self, table_name):
        """
        add trigger for table timestamps
        """

        table_triggers_query = (
            "CREATE TRIGGER set_timestamp"
            + f"\nBEFORE UPDATE ON {table_name}"
            + "\nFOR EACH ROW"
            + "\nEXECUTE PROCEDURE trigger_set_timestamp();")

        print()
        print(table_triggers_query)

        # retrieve migrations
        cur = self.conn.cursor()
        cur.execute(table_triggers_query)

        # commit
        self.conn.commit()

    def destroy_all(self, table_name):
        """
        called by active record
        """

        # query
        destroy_all_query = f"DELETE FROM {table_name};"

        print(destroy_all_query)

        # retrieve migrations
        cur = self.conn.cursor()
        cur.execute(destroy_all_query)

        # commit
        self.conn.commit()
