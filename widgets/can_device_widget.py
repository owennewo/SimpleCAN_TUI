from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from typing import Dict
from config.config import CanDevice


class CanDeviceWidget(Widget):

    table = DataTable(id="device-table")
    table.cursor_type = "row"

    def __init__(self, devices: Dict[int, CanDevice]):
        super().__init__()
        self.devices = devices

    def on_mount(self) -> None:
        self.table.add_column("device", key="device")
        self.table.clear()
        for key, can_device in self.devices.items():
            row = tuple([can_device.name])
            self.table.add_row(*row, key=str(key), label=f"{key:#03x}")

    def compose(self) -> ComposeResult:
        yield self.table
