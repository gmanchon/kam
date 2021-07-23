
from kam.app.models.active_record import ActiveRecord


class {{model_klass_name}}(ActiveRecord):

    def __init__(self, **kwargs):

        # retrieve {{model_klass_name.lower()}} attributes
        self.id = kwargs.get("id"){% for instance_variable, _ in instance_variable_types.items() %}
        self.{{instance_variable}} = kwargs.get("{{instance_variable}}"){% endfor %}

    def __repr__(self):

        return f"#<{{model_klass_name}} @={id(self)} id={self.id}{% for instance_variable, _ in instance_variable_types.items() %} {{instance_variable}}={self.{{instance_variable}}}{% endfor %}>"

