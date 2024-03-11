from textual.app import ComposeResult
from textual.widgets import Label, Input
from textual.widget import Widget
from textual.containers import Horizontal
from textual import on
from simplecan.controller import SimpleCanController
from simplecan.event import SimpleCanEvent
from config.config import Config

from textual.reactive import reactive


class CanFooter(Widget):

    error_count = reactive(0)
    tx_count = reactive(0)
    rx_count = reactive(0)

    last1_rx_name = reactive("?")
    last1_rx_value = reactive(0)

    last2_rx_name = reactive("?")
    last2_rx_value = reactive(0)

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def render(self) -> str:
        return f"rx: {self.rx_count} tx: {self.tx_count} err: {self.error_count}  {self.last1_rx_name}: {self.last1_rx_value} {self.last2_rx_name}: {self.last2_rx_value}"

    @on(SimpleCanEvent)
    def on_simplecan_event(self, event: SimpleCanEvent):
        field_name = self.config.modules[event.module_id].fields[event.field_id].name
        if self.last1_rx_name != field_name:
            self.last2_rx_name = self.last1_rx_name
            self.last2_rx_value = self.last1_rx_value
        self.last1_rx_name = field_name
        self.last1_rx_value = event.value

        if event.msg.is_error_frame:
            self.error_count += 1
        elif event.msg.is_rx:
            self.rx_count += 1

            if self.config.modules[event.module_id].name == "TELEMETRY":
                self.telemetry_values[event.field_id] = event.value
        else:
            self.tx_count += 1
        event.stop()
