from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from typing import Dict
from config.config import CanDevice
from textual.events import Key
from textual import on
from widgets.quit_widget import QuitWidget


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

    @on(Key)
    def on_key(self, event: Key) -> None:
        if event.key == "escape":

            def check_quit(quit: bool) -> None:
                if quit:
                    self.app.exit()

            self.app.push_screen(QuitWidget(), check_quit)

        elif event.key == "enter":
            pass
            # self.app.can_module_widget.table.focus()
        # event.stop()
