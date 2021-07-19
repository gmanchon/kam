
class {{table}}():

    def __init__(self, **kwargs):

        # retrieve {{table.lower()}} attributes
        self.id = kwargs.get("id")
        {% for column, _ in column_types.items()
        %}self.{{column}} = kwargs.get("{{column}}")
        {% endfor %}
    def __repr__(self):

        return f"#<{{table}} @={id(self)} id={self.id} {% for column, _ in column_types.items() %} {{column}}={self.{{column}}}{% endfor %}>"
