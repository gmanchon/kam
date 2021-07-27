
from kam.app.models.active_record_schema import ActiveRecordSchema


def define(self):{% for table_name, columns in table_columns.items() %}

    self.create_table(
        "{{table_name}}",
        dict({% for column in columns %}
            {{column["column"]}}="{{column["data_type"]}}",{% endfor %}
            timestamps=True),
        dict({% for constraint in table_constraints.get(table_name, []) %}
            {{constraint["column"]}}="{{constraint["foreign_table"]}}",{% endfor %})){% endfor %}


ActiveRecordSchema.define(define)

