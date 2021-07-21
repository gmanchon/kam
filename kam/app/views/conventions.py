
import os

from datetime import datetime


def pluralize(model_name):
    """
    process plural form from singular form
    """

    # TODO: pluralize
    return f"{model_name}s"


def singularize(model_name):
    """
    process singular form from plural form
    """

    # TODO: singularize
    return model_name[:-1]


def model_code_file(model_name):
    """
    build model code file name from model name
    """

    return f"{model_name.lower()}.py"


def model_code_file_path(model_name):
    """
    build model code file path from model name
    """

    # TODO: kampai to determine project path
    return os.path.relpath(os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "certif",
        "models",
        model_code_file(model_name)))


def model_migration_file(model_name):
    """
    build model migration file name from model name
    """

    # get current date and time
    now = datetime.now()
    timestamp = datetime.strftime(now, "%Y%m%d%H%M%S")

    return f"{timestamp}_create_{model_name.lower()}.py"


def model_migration_file_path(model_name):
    """
    build model migration file path from model name
    """

    # TODO: kampai to determine project path
    return os.path.relpath(os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "certif",
        "db",
        "migrate",
        model_migration_file(model_name)))
