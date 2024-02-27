from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from simplecan.event import SimpleCanEvent
from textual import on


class CanFieldWidget(Widget):

    field_table = DataTable(id="field-table")
    field_table.cursor_type = "row"

    def on_mount(self) -> None:
        self.field_table.add_column("field", key="field")
        self.field_table.add_column("value", key="value")
        self.field_table.add_column("datatype", key="datatype")
        self.field_table.add_column("description", key="description")

    def compose(self) -> ComposeResult:
        yield self.field_table

    @on(SimpleCanEvent)
    def on_simplecan_event(self, event: SimpleCanEvent):
        self.field_table.update_cell(
            row_key=str(event.field_id), column_key="value", value=event.value
        )
        event.stop()

    def update_fields(self, can_module):
        self.field_table.clear()
        for key, field in can_module.fields.items():
            row = (field.name, field.value, field.datatype, field.description)
            self.field_table.add_row(*row, key=str(key), label=f"{key:#03x}")
