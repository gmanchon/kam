
from kam.app.models.active_record import ActiveRecord


class {{model_klass_name}}(ActiveRecord):

    def __init__(self, **kwargs):

        # retrieve {{model_klass_name.lower()}} attributes
        self.id = kwargs.get("id"){% for instance_variable, data_type in instance_variable_types.items() if data_type != "references" %}
        self.{{instance_variable}} = kwargs.get("{{instance_variable}}"){% endfor %}
        self.created_at = kwargs.get("created_at")
        self.updated_at = kwargs.get("updated_at")

    def __repr__(self):

        return f"#<{{model_klass_name}} @={id(self)} id={self.id}{% for instance_variable, _ in instance_variable_types.items() %} {{instance_variable}}={self.{{instance_variable}}}{% endfor %} created_at={self.created_at} updated_at={self.updated_at}>"

