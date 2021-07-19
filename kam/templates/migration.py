
from kam.app.models.active_record_migration import ActiveRecordMigration


class Create{{model_name}}(ActiveRecordMigration):

    def change(self):

        self.create_table(
            "{{model_name.lower()}}",
            dict({% for instance_variable, data_type in instance_variable_types.items() %}
                {{instance_variable}}="{{data_type}}",{% endfor %}
                timestamps=True))

