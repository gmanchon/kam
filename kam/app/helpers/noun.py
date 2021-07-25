
from kam.app.helpers.grammar import (
    pluralize)

import re


def klass_name_to_table_name(model_klass_name):
    """
    build db table name from model klass name
    """

    table_name = pluralize(klass_name_to_table_ref(model_klass_name))

    return table_name


def klass_name_to_table_ref(model_klass_name):
    """
    build singular table name from model klass name
    """

    table_ref = "_".join(re.findall('[A-Z][^A-Z]*', model_klass_name)).lower()

    return table_ref


def table_ref_to_klass_name(table_name):
    """
    build model klass name from model name
    """

    klass_name = "".join([w.capitalize() for w in table_name.split("_")])

    return klass_name
