from textual.app import ComposeResult
from textual.widgets import Label, Input
from textual.widget import Widget
from textual.containers import Horizontal

# from textual.reactive import Reactive
from textual.reactive import reactive


class CanFooter(Widget):

    error_count = reactive(0)
    tx_count = reactive(0)
    rx_count = reactive(0)

    def render(self) -> str:
        return f"rx: {self.rx_count} tx: {self.tx_count} err: {self.error_count}"

    def on_can_message(self, msg):
        if msg.is_error_frame:
            self.error_count += 1
        elif msg.is_rx:
            self.rx_count += 1
        else:
            self.tx_count += 1
