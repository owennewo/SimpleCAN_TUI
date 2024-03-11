from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from typing import Dict
from config.config import CanModule
from textual.events import Key
from textual import on


class CanModuleWidget(Widget):

    table = DataTable(id="module-table")
    table.cursor_type = "row"

    def __init__(self, modules: Dict[int, CanModule]):
        super().__init__()
        self.modules = modules

    def on_mount(self) -> None:
        self.table.add_column("module", key="name")
        self.table.clear()
        for key, can_module in self.modules.items():
            row = tuple([can_module.name])
            self.table.add_row(*row, key=str(key), label=f"{key:#03x}")

    def compose(self) -> ComposeResult:
        yield self.table

    @on(Key)
    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.app.can_device_widget.table.focus()
        elif event.key == "enter":
            pass
            # 
        # event.stop()
