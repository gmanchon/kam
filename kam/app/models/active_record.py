
from kam.app.controllers.database_controller import instantiate_db
from kam.app.models.active_record_schema import ActiveRecordSchema

from kam.app.views.conventions import (
    model_to_db_table,
    singularize,
    is_plural,
    model_name_to_klass_name,
    schema_file_path,
    model_to_db_table_ref)

import os

import importlib


class ActiveRecord():

    # retrieve db connection
    db = instantiate_db()

    def __load_db_schema():
        """
        load schema into class variable
        """

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

    # references
    one = {}
    many = {}

    @classmethod
    def __get_model_klass(cls, model_name):

        model_sing_name = singularize(model_name) if is_plural(model_name) else model_name

        # build class name
        klass_name = model_name_to_klass_name(model_sing_name)

        # build module name
        klass_module_name = ".".join(cls.__module__.split(".")[:-1] + [model_sing_name])

        # import module
        klass_module = importlib.import_module(klass_module_name)

        # get klass
        model_klass = getattr(klass_module, klass_name)

        return model_klass

    @classmethod
    def belongs_to(cls, model_name, through=None):

        # get model klass
        model_klass = cls.__get_model_klass(model_name)

        # store reference
        child_klass_name = cls.__name__
        klass_ones = cls.one.get(child_klass_name, {})
        klass_ones[model_name] = dict(
            klass=model_klass,
            through=through)
        cls.one[child_klass_name] = klass_ones

    @classmethod
    def has_many(cls, model_names, through=None):

        # get model klass
        model_name = singularize(model_names)
        model_klass = cls.__get_model_klass(model_name)

        # store reference
        child_klass_name = cls.__name__
        klass_manys = cls.many.get(child_klass_name, {})
        klass_manys[model_names] = dict(
            klass=model_klass,
            through=through)
        cls.many[child_klass_name] = klass_manys

    def __getattr__(self, name):
        """
        handle missing method calls for belongs_to and has_many relationships
        """

        def _missing(*args, **kwargs):
            """
            call relation method if it exists
            """

            # look out for belongs_to relationships
            relation_model = None
            child_klass_name = type(self).__name__

            # retrieve reference klasses
            klass_ones = self.one.get(child_klass_name, {})
            klass_manys = self.many.get(child_klass_name, {})

            if name in klass_ones.keys():

                # retrieve relation model
                relation_model = klass_ones[name]

            elif name in klass_manys.keys():

                # retrieve relation model
                relation_model = klass_manys[name]

            else:

                # alert missing method
                raise ValueError(f"Missing method {name} for {self}, {args}, {kwargs} 🤒")

            # check if a relation exists
            if relation_model is not None:

                # retrieve klass
                relation_klass = relation_model["klass"]
                relation_through = relation_model["through"]

                if relation_through is None:
                    relation_through = [name]

                # build class id
                klass_name = type(self).__name__
                klass_rel = model_to_db_table_ref(klass_name)

                # retrieve linked objects
                relations = self.where(
                    **dict(id=self.id),
                    through=relation_through)  # + [name])

                # fill self reference
                for relation in relations:
                    setattr(relation, klass_rel, self)

                return relations

        return _missing

    def _repr_html_(self):
        """
        allow visual representation of objects in streamlit
        """

        # TODO: handle when called on class rather than object (type does not display)

        return self

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

    @classmethod
    def all(cls):
        """
        return all rows
        """

        # get child class name
        child_klass_name = cls.__name__
        table_name = model_to_db_table(child_klass_name)

        print(f"\nreturn all rows from {table_name}...")

        # retrieve rows
        all_rows = cls.db.select_all(table_name)

        # convert rows to model instances
        converted_rows = [cls(**row) for row in all_rows]

        return converted_rows

    @classmethod
    def where(cls, through=[], **kwargs):
        """
        return matching rows
        """

        # get child class name
        child_klass_name = cls.__name__
        table_name = model_to_db_table(child_klass_name)

        print(f"\nreturn matching rows for {kwargs} from {table_name}...")

        # retrieve table schema
        table_schema = ActiveRecordSchema.db_schema[table_name]

        # retrieve rows
        matching_rows, target_table = cls.db.select_where(
            table_name, table_schema, **kwargs, through=through)

        # get model klass
        model_klass = cls.__get_model_klass(target_table)

        # convert rows to model instances
        converted_rows = [model_klass(**row) for row in matching_rows]

        return converted_rows

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
