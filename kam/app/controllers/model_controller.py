
from kam.app.views.conventions import table_to_model_python_file_path

from jinja2 import Environment, PackageLoader, select_autoescape


DATA_TYPE_STRING = "string"
DATA_TYPE_INTEGER = "integer"
DATA_TYPE_REFERENCES = "references"

SUPPORTED_DATA_TYPES = [
    DATA_TYPE_STRING,
    DATA_TYPE_INTEGER,
    DATA_TYPE_REFERENCES]


def __create_model_migration_file(env, table, instance_variable_types):
    """
    create model migration file
    """

    # retrieve model template
    model_template = env.get_template("migration.py")

    # apply template
    model_code = model_template.render(
        table=table,
        column_types=instance_variable_types)

    # build model path
    model_target_path = table_to_model_python_file_path(table)

    # write model
    with open(model_target_path, "w") as file:
        file.write(model_code)

    print(f"# wrote {model_target_path}")


def __create_model_code_file(env, table, instance_variable_types):
    """
    create model code file
    """

    # retrieve model template
    model_template = env.get_template("model.py")

    # apply template
    model_code = model_template.render(
        table=table,
        column_types=instance_variable_types)

    # build model path
    model_target_path = table_to_model_python_file_path(table)

    # write model
    with open(model_target_path, "w") as file:
        file.write(model_code)

    print(f"# wrote {model_target_path}")


def create(model_name, instance_variables):
    """
    validate model name and instance variables naming conventions
    create model code file
    create model migration
    """

    # validate table case
    if model_name[:1] != model_name[:1].upper():
        raise ValueError(f"Model name {model_name} should follow the UpperCamelCase naming convention 🤒")

    print(f"{model_name}:")

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
    __create_model_migration_file(env, model_name, instance_variable_types)

    # create model code file
    __create_model_code_file(env, model_name, instance_variable_types)
