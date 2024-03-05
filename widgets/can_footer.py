from textual.app import ComposeResult
from textual.widgets import Label, Input
from textual.widget import Widget
from textual.containers import Horizontal
from textual import on
from simplecan.controller import SimpleCanController
from simplecan.event import SimpleCanEvent
from config.config import Config

# from textual.reactive import Reactive
from textual.reactive import reactive


class CanFooter(Widget):

    error_count = reactive(0)
    tx_count = reactive(0)
    rx_count = reactive(0)
    telemetry_values = reactive([0, 0, 0, 0])

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def render(self) -> str:
        return f"rx: {self.rx_count} tx: {self.tx_count} err: {self.error_count}   [0={self.telemetry_values[0]:.2f}] [1={self.telemetry_values[1]:.2f}] [2={self.telemetry_values[2]:.2f}] [3={self.telemetry_values[3]:.2f}]"

    @on(SimpleCanEvent)
    def on_simplecan_event(self, event: SimpleCanEvent):
        if event.msg.is_error_frame:
            self.error_count += 1
        elif event.msg.is_rx:
            self.rx_count += 1

            if self.config.modules[event.module_id].name == "TELEMETRY":
                self.telemetry_values[event.field_id] = event.value
        else:
            self.tx_count += 1
        event.stop()
