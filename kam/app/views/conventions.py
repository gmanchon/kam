
import os


def table_to_model_python_file(model_name):
    """
    build model python file name from model name
    """

    return f"{model_name.lower()}.py"


def table_to_model_python_file_path(model_name):
    """
    build model python file path from model name
    """

    # TODO: kampai to determine project path
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "certif",
        "models",
        table_to_model_python_file(model_name))
