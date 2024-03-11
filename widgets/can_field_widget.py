from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from simplecan.event import SimpleCanEvent
from textual import on
import asyncio
from textual.events import Key
from widgets.can_field_edit_widget import CanFieldEditWidget


class CanFieldWidget(Widget):

    table = DataTable(id="field-table")
    table.cursor_type = "row"
    update_lock = asyncio.Lock()

    def on_mount(self) -> None:
        self.table.add_column("field", key="field")
        self.table.add_column("value", key="value")
        self.table.add_column("datatype", key="datatype")
        self.table.add_column("description", key="description")

    def compose(self) -> ComposeResult:
        yield self.table

    @on(SimpleCanEvent)
    async def on_simplecan_event(self, event: SimpleCanEvent):
        if event.module_id != self.app.module_id:
            return
        async with self.update_lock:
            self.table.update_cell(
                row_key=str(event.field_id),
                column_key="value",
                value=event.value,
                update_width=True,
            )

            coordinate = self.table.get_cell_coordinate(
                row_key=str(event.field_id), column_key="value"
            )
            self.table.move_cursor(
                row=coordinate.row, column=coordinate.column, animate=False
            )
            self.table.refresh_row(coordinate.row)
            await asyncio.sleep(
                0.04
            )  # this sleep is just to slow things down to see the cursor move
            event.stop()

    async def delayed_push_screen(self):
        await asyncio.sleep(0.01)
        self.app.push_screen(
            CanFieldEditWidget(
                self.app.config,
                self.app.device_id,
                self.app.module_id,
                self.app.field_id,
            )
        )

    @on(Key)
    async def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.app.can_module_widget.table.focus()
        elif event.key == "enter":
            asyncio.create_task(self.delayed_push_screen())

    def update_fields(self, can_module):
        self.table.clear()
        for key, field in can_module.fields.items():
            row = (field.name, field.value, field.datatype, field.description)
            self.table.add_row(*row, key=str(key), label=f"{key:#03x}")
