
from kam.app.models.base_database import BaseDatabase

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
