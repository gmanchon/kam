
from kam.app.helpers.grammar import (pluralize,
                                     singularize,
                                     is_plural)


class TestGrammar:

    def test_pluralize(self):
        """
        test noun pluralize
        """

        # plural rules
        nouns = dict(

            # # invariant exceptions
            # fish="fish",
            # deer="deer",

            # exceptions
            child="children",
            mouse="mice",

            # change y to ies if y is preceded by consonant
            candy="candies",
            puppy="puppies",

            # add es to consonant before an o
            potato="potatoes",
            tomato="tomatoes",

            # add s if y is preceded by vowel
            toy="toys",
            monkey="monkeys",

            # add es to nouns ending in ch, sh, s, x or z
            bench="benches",
            dish="dishes",
            bus="buses",
            box="boxes",
            quizz="quizzes",

            # change f or fe to ves
            loaf="loavs",  # volontary plural error
            knife="knives",

            # add s to nouns
            apple="apples",
            girl="girls")

        for singular, plural in nouns.items():

            pluralized = pluralize(singular)
            singularized = singularize(plural)

            assert is_plural(singular) is False
            assert is_plural(plural) is True

            assert pluralized == plural, f"bad plural for {singular}"
            assert singularized == singular, f"bad singular for {plural}"
