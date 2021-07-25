
def pluralize(noun):
    """
    process plural form from singular form
    """

    # TODO: pluralize
    return f"{noun}s"


def singularize(noun):
    """
    process singular form from plural form
    """

    # TODO: singularize
    return noun[:-1]


def is_plural(noun):
    """
    determines whether noun is plural
    """

    # TODO: is plural
    # TODO: does not work if singular class ends by an s
    return noun[-1:].lower() == "s"
