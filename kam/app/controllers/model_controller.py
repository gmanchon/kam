
from jinja2 import Environment, PackageLoader, select_autoescape


DATA_TYPE_STRING = "string"
DATA_TYPE_INTEGER = "integer"
DATA_TYPE_REFERENCES = "references"

SUPPORTED_DATA_TYPES = [
    DATA_TYPE_STRING,
    DATA_TYPE_INTEGER,
    DATA_TYPE_REFERENCES]


def create(table, column_types):
    """
    create model code
    """

    # validate table case
    if table[:1] != table[:1].upper():
        raise ValueError(f"Table name {table} should follow the UpperCamelCase naming convention 🤒")

    print(f"{table}:")

    # validate column parameters
    for column_type in column_types:

        # retrieve column and data type
        column, data_type = column_type.split(":")

        # validate column case
        if column != column.lower():
            raise ValueError(f"Column name {column} should follow the snake_case naming convention 🤒")

        # validate data type
        if data_type not in SUPPORTED_DATA_TYPES:
            raise ValueError(f"Invalid data type {data_type}, supported: {', '.join(SUPPORTED_DATA_TYPES)} 🤒")

        print(f"- {column} ({data_type})")

    # create templating environment
    env = Environment(
        loader=PackageLoader("kam"),
        autoescape=select_autoescape()
    )

    # retrieve model template
    model_template = env.get_template("model.py")

    # convert params
    table_column_types = {c: t for c, t in [ct.split(":") for ct in column_types]}

    print(table_column_types)

    # apply template
    model_code = model_template.render(
        table=table,
        column_types=table_column_types)

    print(model_code)
