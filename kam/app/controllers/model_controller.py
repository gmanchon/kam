
from kam.app.views.conventions import (
    pluralize,
    model_code_file_path,
    model_migration_file_path,
    model_to_db_table)

import os

from jinja2 import Environment, PackageLoader, select_autoescape


DATA_TYPE_STRING = "string"
DATA_TYPE_TEXT = "text"
DATA_TYPE_INTEGER = "integer"
DATA_TYPE_REFERENCES = "references"

SUPPORTED_DATA_TYPES = [
    DATA_TYPE_STRING,
    DATA_TYPE_TEXT,
    DATA_TYPE_INTEGER,
    DATA_TYPE_REFERENCES]

TEMPLATE_MIGRATION_FILENAME = "migration.py"
TEMPLATE_MODEL_FILENAME = "model.py"


def __create_model_template(env, template_name, model_klass_name, instance_variable_types):
    """
    create model template file
    """

    # retrieve model template
    model_template = env.get_template(template_name)

    # apply template
    model_code = model_template.render(
        model_klass_name=model_klass_name,
        model_table_name=model_to_db_table(model_klass_name),
        migration_klass_name=pluralize(model_klass_name),
        instance_variable_types=instance_variable_types)

    # select target file path
    target_file_path_function = {
        TEMPLATE_MIGRATION_FILENAME: model_migration_file_path,
        TEMPLATE_MODEL_FILENAME: model_code_file_path}

    # build model path
    model_target_path = target_file_path_function[template_name](model_klass_name)

    # create directory
    os.makedirs(os.path.dirname(model_target_path), exist_ok=True)

    # write model
    with open(model_target_path, "w") as file:
        file.write(model_code)

    print(f"# wrote {model_target_path}")


def create(model_klass_name, instance_variables):
    """
    validate model name and instance variables naming conventions
    create model code file
    create model migration
    """

    # validate model name case
    if "_" in model_klass_name or model_klass_name[:1] != model_klass_name[:1].upper():
        raise ValueError(f"Model name {model_klass_name} should follow the UpperCamelCase naming convention 🤒")

    print(f"{model_klass_name}:")

    # validate column parameters
    for column_type in instance_variables:

        # retrieve column and data type
        column, data_type = column_type.split(":")

        # validate column case
        if column != column.lower():
            raise ValueError(f"Column name {column} should follow the snake_case naming convention 🤒")

        # validate data type
        if data_type not in SUPPORTED_DATA_TYPES:
            raise ValueError(f"Invalid data type {data_type}, supported: {', '.join(SUPPORTED_DATA_TYPES)} 🤒")

        print(f"- {column} ({data_type})")

    # convert params
    instance_variable_types = {c: t for c, t in [ct.split(":") for ct in instance_variables]}

    # create templating environment
    env = Environment(
        loader=PackageLoader("kam"),
        autoescape=select_autoescape()
    )

    # create model migration file
    __create_model_template(env, TEMPLATE_MIGRATION_FILENAME, model_klass_name, instance_variable_types)

    # create model code file
    __create_model_template(env, TEMPLATE_MODEL_FILENAME, model_klass_name, instance_variable_types)
