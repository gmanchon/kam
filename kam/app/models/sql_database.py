
from kam.app.models.base_database import BaseDatabase

from kam.app.controllers.model_controller import SUPPORTED_DATA_TYPES

from kam.app.helpers.grammar import (
    singularize,
    pluralize,
    is_plural)

from kam.app.helpers.database import (
    retrieve_table_alias)

from kam.app.helpers.file import (
    schema_file_path)

import os
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor

from jinja2 import Environment, PackageLoader, select_autoescape

TEMPLATE_SCHEMA_FILENAME = "schema.py"

DB_TO_KAM_DATATYPE = dict(
                int8="integer",
                varchar="string",
                text="string",
                timestamptz="string")


class SqlDatabase(BaseDatabase):

    TIMESTAMP_COLUMNS = ["created_at", "updated_at"]

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

    def __create_schema_template(self, env, template_name, table_columns):
        """
        create schema template file
        """

        # retrieve schema template
        schema_template = env.get_template(template_name)

        # apply template
        schema_code = schema_template.render(
            table_columns=table_columns)

        # build schema path
        schema_target_path = schema_file_path()

        # create directory
        os.makedirs(os.path.dirname(schema_target_path), exist_ok=True)

        # write schema
        with open(schema_target_path, "w") as file:
            file.write(schema_code)

        print(f"\n# wrote {schema_target_path}")

    def _dump_schema_columns(self, schema_columns):
        """
        dump schema columns
        """

        # create templating environment
        env = Environment(
            loader=PackageLoader("kam"),
            autoescape=select_autoescape()
        )

        # convert schema columns to table columns
        table_columns = {}

        for table, position, column, nullable, udt_name in schema_columns:

            # retrieve table content
            table_content = table_columns.get(table, [])
            table_columns[table] = table_content

            # convert data type
            data_type = DB_TO_KAM_DATATYPE[udt_name]

            # fille table content
            table_content.append(dict(
                position=position,
                column=column,
                nullable=nullable,
                data_type=data_type))

        # create model migration file
        self.__create_schema_template(env, TEMPLATE_SCHEMA_FILENAME, table_columns)

    def dump_schema(self):
        """
        dump database schema
        """

        # query
        query_schema = (
            "SELECT table_name, ordinal_position, column_name, is_nullable, udt_name"
            + "\nFROM information_schema.columns"
            + f"\nWHERE table_catalog = '{self.dbname}'"
            + "\nAND table_schema = 'public'"
            + "\nORDER BY table_name, ordinal_position;")

        print()
        print(query_schema)

        # create trigger
        cur = self.conn.cursor()
        cur.execute(query_schema)

        # fetch results
        schema_columns = cur.fetchall()

        # dump schema columns
        self._dump_schema_columns(schema_columns)

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
            elif data_type == "text":
                statements.append(f"\"{column}\" TEXT NULL")
            elif data_type == "integer":
                statements.append(f"\"{column}\" BIGINT NULL")
            elif data_type == "references":
                statements.append(f"{column}_id BIGSERIAL NOT NULL")
            else:
                raise ValueError(f"Invalid data type {data_type}, supported: {', '.join(SUPPORTED_DATA_TYPES)} 🤒")

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

    def select_all(self, table_name):
        """
        called by active record
        """

        # query
        select_all_query = f"SELECT * FROM {table_name};"

        print(select_all_query)

        # retrieve migrations
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(select_all_query)

        # fetch results
        all_rows = cur.fetchall()

        return all_rows

    def select_where(self, model_table_name, table_schema, through=[], **kwargs):
        """
        called by active record
        """

        # retrieve table aliases
        model_alias, through_alias = retrieve_table_alias(
            model_table_name, through)

        # build target alias
        target_alias = model_alias if len(through) == 0 else through_alias[-1]
        target_table = model_table_name if len(through) == 0 else through[-1]

        # query
        select_all_query = (
            f"SELECT {target_alias}.*"
            + f"\nFROM {model_table_name} {model_alias}")

        # iterate through join tables
        previous_table = singularize(model_table_name) if is_plural(model_table_name) else model_table_name
        previous_alias = model_alias
        for join_table, join_alias in zip(through, through_alias):

            # check relation direction
            if is_plural(join_table):

                select_all_query += (
                    f"\nJOIN {join_table} {join_alias} "
                    + f"ON {join_alias}.\"{previous_table}_id\" "
                    + f"= {previous_alias}.id")

            else:

                select_all_query += (
                    f"\nJOIN {pluralize(join_table)} {join_alias} "
                    + f"ON {join_alias}.id "
                    + f"= {previous_alias}.\"{join_table}_id\"")

            # set next alias
            previous_table = singularize(join_table) if is_plural(join_table) else join_table
            previous_alias = join_alias

        # filters
        select_all_query += "\nWHERE"

        # iterate through arguments
        where_clauses = []

        for column, value in kwargs.items():

            # get column data type
            column_data_type = table_schema[column]

            # fill value
            if column_data_type == "string":
                where_clauses.append(f"\n{model_alias}.\"{column}\" = '{value}'")
            elif column_data_type == "integer":
                where_clauses.append(f"\n{model_alias}.\"{column}\" = {value}")

        # join where clauses
        select_all_query += (
            "\nAND".join(where_clauses)
            + ";")

        print(select_all_query)

        # retrieve migrations
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(select_all_query)

        # fetch results
        matching_rows = cur.fetchall()

        # TODO: handle references

        return matching_rows, target_table

    def insert(self, table_name, table_schema, active_record, columns):
        """
        called by active record
        """

        # query
        insert_query = f"INSERT INTO {table_name} ("

        # iterate through column names
        column_names = []

        for column in columns.keys():

            # skip timestamp columns
            if column in SqlDatabase.TIMESTAMP_COLUMNS:
                continue

            column_names.append(f"\"{column}\"")

        insert_query += ", ".join(column_names)

        # add separator
        insert_query += "\n) VALUES ("

        # iterate through column values
        column_values = []

        for index, value in enumerate(columns.values()):

            # get column data type
            column = list(columns.keys())[index]
            column_data_type = table_schema[column]

            # skip timestamp columns
            if column in SqlDatabase.TIMESTAMP_COLUMNS:
                continue

            # fill value
            if column_data_type == "string":
                column_values.append(f"'{value}'")
            elif column_data_type == "integer":
                column_values.append(f"{value}")

        insert_query += ", ".join(column_values)

        # add end
        insert_query += "\n) RETURNING id;"

        print(insert_query)

        # retrieve migrations
        cur = self.conn.cursor()
        cur.execute(insert_query)

        # retrieve inserted id
        insert_res = cur.fetchone()
        active_record.id = insert_res[0]

        # commit
        self.conn.commit()

    def update(self, table_name, table_schema, id, columns):
        """
        called by active record
        """

        # query
        update_query = f"UPDATE {table_name} SET"

        # iterate through columns
        update_rows = []

        for column, value in columns.items():

            # skip timestamp columns
            if column in SqlDatabase.TIMESTAMP_COLUMNS:
                continue

            # get column data type
            column_data_type = table_schema[column]

            # fill value
            if column_data_type == "string":
                update_rows.append(f"\n\"{column}\" = '{value}'")
            elif column_data_type == "integer":
                update_rows.append(f"\n\"{column}\" = {value}")

        update_query += ", ".join(update_rows)

        # add separator
        update_query += f"\nWHERE id = {id};"

        print(update_query)

        # retrieve migrations
        cur = self.conn.cursor()
        cur.execute(update_query)

        # commit
        self.conn.commit()
