
DATA_TYPE_STRING = "string"
DATA_TYPE_INTEGER = "integer"
DATA_TYPE_REFERENCES = "references"

SUPPORTED_DATA_TYPES = [
    DATA_TYPE_STRING,
    DATA_TYPE_INTEGER,
    DATA_TYPE_REFERENCES]


def create(table, columns):
    """
    create model code
    """

    # validate table case
    if table[:1] != table[:1].upper():
        raise ValueError(f"Table name {table} should follow the UpperCamelCase naming convention 🤒")

    print(f"{table}:")

    # validate column parameters
    for column_parameter in columns:

        # retrieve column and data type
        column, data_type = column_parameter.split(":")

        # validate column case
        if column != column.lower():
            raise ValueError(f"Column name {column} should follow the snake_case naming convention 🤒")

        # validate data type
        if data_type not in SUPPORTED_DATA_TYPES:
            raise ValueError(f"Invalid data type {data_type}, supported: {', '.join(SUPPORTED_DATA_TYPES)} 🤒")

        print(f"- {column} ({data_type})")
