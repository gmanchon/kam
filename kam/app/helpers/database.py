
def retrieve_table_alias(source_table_name, through):
    """
    return unique table aliases
    """

    # build table list
    tables = [source_table_name] + through
    aliases = []

    # iterate through tables
    for table in tables:

        # search for alias, full table name should be enough at worst at the moment
        alias_candidate = None
        for index in range(len(table)):

            # build alias candidate
            alias_candidate = table[:index + 1]

            # test alias availability
            if alias_candidate not in aliases:

                # alias is valid
                break

        # store alias
        aliases.append(alias_candidate)

    return aliases[0], aliases[1:]


if __name__ == '__main__':

    source_alias, through_alias = retrieve_table_alias(
        "a_test_table", through=["abc", "abcdef", "b"])
    print(source_alias, through_alias)
