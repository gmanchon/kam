"""
deterministic grammar
"""


def _revert(dictionary):
    """
    revert dictionary keys and values
    """

    return {v: k for k, v in dictionary.items()}

# unhandled (impossible to determine singular from plural)
# INVARIANT_EXCEPTIONS = dict(  # unhandled
#     fish="fish",
#     deer="deer")


PLURAL_EXCEPTIONS = [
    "bus"]

EXCEPTIONS = dict(
    child="children",
    mouse="mice")

R_EXCEPTIONS = _revert(EXCEPTIONS)

CONSONANT_RULES = dict(
    y="ies",
    o="oes")

R_CONSONANT_RULES = _revert(CONSONANT_RULES)

VOWEL_RULES = dict(
    y="ys")

R_VOWEL_RULES = _revert(VOWEL_RULES)

PLURAL_RULES = dict(
    ch="ches",
    sh="shes",
    s="ses",
    x="xes",
    z="zes",
    f="vs",  # volontary error to revert to singular (should be "ves")
    fe="ves")

R_PLURAL_RULES = _revert(PLURAL_RULES)

ALL = dict(CONSONANT_RULES, **VOWEL_RULES)
ALL.update(PLURAL_RULES)

R_ALL = dict(R_CONSONANT_RULES, **R_VOWEL_RULES)
R_ALL.update(**R_PLURAL_RULES)


def pluralize(noun):
    """
    process plural form from singular form
    """

    if noun in EXCEPTIONS:
        return EXCEPTIONS[noun]

    end_letter = noun[-1]
    prev_letter = noun[-2]

    if end_letter in CONSONANT_RULES and _is_consonant(prev_letter):
        return f"{noun[:-1]}{CONSONANT_RULES[end_letter]}"

    if end_letter in VOWEL_RULES and _is_vowel(prev_letter):
        return f"{noun[:-1]}{VOWEL_RULES[end_letter]}"

    for suffix, plural in PLURAL_RULES.items():
        if noun[-len(suffix):] == suffix:
            return f"{noun[:-len(suffix)]}{plural}"

    if end_letter == "y":
        return f"{noun[:-1]}ies"

    return f"{noun}s"


def singularize(noun):
    """
    process singular form from plural form
    """

    if noun in R_EXCEPTIONS:
        return R_EXCEPTIONS[noun]

    for suffix, singular in R_ALL.items():
        if noun[-len(suffix):] == suffix:
            return f"{noun[:-len(suffix)]}{singular}"

    if noun[-3:] == "ies":
        return f"{noun[:-3]}y"

    return noun[:-1]


def is_plural(noun):
    """
    determines whether noun is plural
    """

    if noun in PLURAL_EXCEPTIONS:
        return False

    if noun in R_EXCEPTIONS:
        return True

    for suffix, singular in R_ALL.items():
        if noun[-len(suffix):] == suffix:
            return True

    if noun[-3:] == "ies":
        return True

    # TODO: does not work if singular class ends by an s
    return noun[-1:].lower() == "s"


def _is_vowel(letter):
    return letter in ["a", "e", "i", "o", "u", "y"]


def _is_consonant(letter):
    return not _is_vowel(letter)
