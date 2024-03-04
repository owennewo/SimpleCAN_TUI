from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input
from textual.containers import Container, Horizontal
from textual import on
from config.config import Config
from textual.events import Key


class CanFieldEditWidget(ModalScreen):

    def __init__(self, config: Config, device_id, module_id, field_id):
        super().__init__()
        self.config = config
        self.device_id = device_id
        self.module_id = module_id
        self.field_id = field_id
        self.field = self.config.modules[self.module_id].fields[self.field_id]
        self.jog_exponent = 0  # 10 ** jog_exponent is the amout we jog

    def compose(self) -> ComposeResult:
        deviceName = self.config.devices[self.device_id].name
        moduleName = self.config.modules[self.module_id].name
        fieldName = self.field.name
        datatype = self.field.datatype
        value = self.field.value
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
                yield Input(str(value), id="input-value")
                yield Label("jog:   ")
                yield Input(str(10**self.jog_exponent), id="input-jog")
            with Horizontal():
                yield Button("update", id="update", variant="success")
                yield Button("close", id="close", variant="error")

    @on(Button.Pressed, "#update")
    def update_field(self) -> None:
        value = self.query_one("#input-value").value
        datatype = self.field.datatype
        self.app.can_controller.send(
            self.device_id,
            self.module_id,
            self.field_id,
            is_rtr=False,
            datatype=datatype,
            value=value,
        )

    @on(Button.Pressed, "#close")
    def close_popup(self) -> None:
        self.app.pop_screen()

    @on(Key)
    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.close_popup()
        elif event.key == "enter":
            self.update_field()
        elif event.key == "up":
            if self.field.datatype == "bool":
                self.query_one("#input-value").value = "True"
            elif self.field.datatype == "float":
                value = float(self.query_one("#input-value").value)
                decimal_places = 1 if self.jog_exponent >= 0 else (-self.jog_exponent)
                self.query_one("#input-value").value = format(
                    (float(value) + 10.0**self.jog_exponent),
                    f".{decimal_places}f",
                )
        elif event.key == "down":
            if self.field.datatype == "bool":
                self.query_one(
                    "#input-value",
                ).value = "False"
            elif self.field.datatype == "float":
                value = float(self.query_one("#input-value").value)
                decimal_places = 1 if self.jog_exponent >= 0 else (-self.jog_exponent)
                self.query_one("#input-value").value = format(
                    (float(value) - 10.0**self.jog_exponent),
                    f".{decimal_places}f",
                )

        elif event.key == "left":
            self.jog_exponent = self.jog_exponent + 1
            self.query_one("#input-jog").value = str(10.0**self.jog_exponent)
        elif event.key == "right":
            self.jog_exponent = self.jog_exponent - 1
            self.query_one("#input-jog").value = str(10.0**self.jog_exponent)
