
from kam.app.models.active_record_migration import ActiveRecordMigration


class Create{{migration_klass_name}}(ActiveRecordMigration):

    def change(self):

        self.create_table(
            "{{model_table_name}}",
            dict({% for instance_variable, data_type in instance_variable_types.items() %}
                {{instance_variable}}="{{data_type}}",{% endfor %}
                timestamps=True))

