from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input
from textual.containers import Container, Horizontal
from textual import on
from config.config import Config


class CanFieldEditWidget(ModalScreen):

    def __init__(self, config: Config, device_id, module_id, field_id):
        super().__init__()
        self.config = config
        self.device_id = device_id
        self.module_id = module_id
        self.field_id = field_id

    def compose(self) -> ComposeResult:
        deviceName = self.config.devices[self.device_id].name
        moduleName = self.config.modules[self.module_id].name
        field = self.config.modules[self.module_id].fields[self.field_id]
        fieldName = field.name
        datatype = field.datatype
        value = field.value
        with Container():
            with Horizontal():
                yield Label("device:  ")
                yield Label(deviceName)
            with Horizontal():
                yield Label("module:  ")
                yield Label(moduleName)
            with Horizontal():
                yield Label("module:  ")
                yield Label(fieldName)
            with Horizontal():
                yield Label("datatype:")
                yield Label(datatype)
            with Horizontal():
                yield Label("value:   ")
                yield Input(str(value))
            with Horizontal():
                yield Button("update", id="update", variant="success")
                yield Button("close", id="close", variant="error")

    @on(Button.Pressed, "#update")
    def exit_app(self) -> None:
        # self.app.exit()
        self.can_controller.send(
            self.device_id, self.module_id, self.field_id, is_rtr=True
        )

    @on(Button.Pressed, "#close")
    def back_to_app(self) -> None:
        self.app.pop_screen()
