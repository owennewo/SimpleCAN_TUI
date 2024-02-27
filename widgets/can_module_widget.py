from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from typing import Dict
from config.config import CanModule


class CanModuleWidget(Widget):

    module_table = DataTable(id="module-table")
    module_table.cursor_type = "row"

    def __init__(self, modules: Dict[int, CanModule]):
        super().__init__()
        self.modules = modules

    def on_mount(self) -> None:
        self.module_table.add_column("module", key="name")
        self.module_table.clear()
        for key, can_module in self.modules.items():
            row = tuple([can_module.name])
            self.module_table.add_row(*row, key=str(key), label=f"{key:#03x}")

    def compose(self) -> ComposeResult:
        yield self.module_table
