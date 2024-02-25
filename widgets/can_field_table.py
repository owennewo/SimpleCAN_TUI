from textual.app import ComposeResult
from textual.widgets import Label, Input
from textual.widget import Widget
from textual.containers import Horizontal
from textual.reactive import Reactive


class CanFieldTable(Widget):

    def compose(self) -> ComposeResult:
        yield Horizontal(Label(f"rx={self.rx_count}, tx={self.tx_count}"))
