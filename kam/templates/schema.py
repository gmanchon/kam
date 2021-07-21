
from kam.app.models.active_record_schema import ActiveRecordSchema


def define(self):{% for table_name, table_columns in table_columns.items() %}

    self.create_table(
        "{{table_name}}",
        dict({% for column in table_columns %}
            {{column["column"]}}="{{column["data_type"]}}",{% endfor %}
            timestamps=True)){% endfor %}


ActiveRecordSchema.define(define)

