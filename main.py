from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, DataTable
from textual.containers import Vertical, Horizontal, Container
from textual import on
from widgets.can_footer import CanFooter
from widgets.can_device_widget import CanDeviceWidget
from widgets.can_module_widget import CanModuleWidget
from widgets.can_field_widget import CanFieldWidget

from simplecan.controller import SimpleCanController
from simplecan.event import SimpleCanEvent
from config.config import (
    load_config_from_yaml,
)
from can.interface import Bus


class VerticalLayoutExample(App):

    CSS_PATH = "main.css"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.device_id = 0
        config = load_config_from_yaml()
        self.can_footer = CanFooter(config)
        self.config = config
        self.modules = config.modules
        self.can_module_widget = CanModuleWidget(self.modules)
        self.module_id = list(config.modules.keys())[0]
        self.can_device_widget = CanDeviceWidget(config.devices)
        self.can_field_widget = CanFieldWidget()
        self.can_controller = SimpleCanController(
            self, config.connection, config.modules
        )

    def compose(self) -> ComposeResult:
        yield Vertical(
            Header(),
            Horizontal(
                Vertical(
                    Container(self.can_device_widget, id="device-container"),
                    Container(self.can_module_widget, id="module-container"),
                    id="vertical-left",
                ),
                Container(self.can_field_widget, id="field-container"),
                id="horizontal-layout",
            ),
            self.can_footer,
            id="vertical-main",
        )

    def request_fields(self):
        mod = self.modules[self.module_id]
        for field_id, _ in mod.fields.items():
            self.can_controller.send(self.device_id, self.module_id, field_id)

    def on_mount(self) -> None:
        self.title = "SimpleCAN_TUI"
        self.sub_title = "For cybergear"
        self.can_field_widget.update_fields(self.modules[self.module_id])
        self.request_fields()

    @on(DataTable.RowSelected, "#device-table")
    def device_selected(self, event):
        self.device_id = int(event.row_key.value)

    @on(DataTable.RowSelected, "#module-table")
    def module_selected(self, event):
        self.module_id = int(event.row_key.value)
        self.can_field_widget.update_fields(self.modules[self.module_id])
        self.request_fields()

    @on(DataTable.RowSelected, "#field-table")
    def field_selected(self, event):
        self.field_id = int(event.row_key.value)

    @on(SimpleCanEvent)
    def can_receive(self, event: SimpleCanEvent):
        self.modules[event.module_id].fields[event.field_id].value = event.value
        self.can_footer.post_message(event)
        if event.msg.is_rx and not event.msg.is_error_frame:
            self.can_field_widget.post_message(event)


app = VerticalLayoutExample()


if __name__ == "__main__":
    app._closing
    app.run()
