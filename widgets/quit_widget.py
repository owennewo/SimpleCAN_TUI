from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual import on
from textual.events import Key


class QuitWidget(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Label("Are you sure you want to quit?", id="question")
                with Horizontal():
                    yield Button("Quit", variant="error", id="quit")
                    yield Button("Cancel", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)

    @on(Key)
    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(False)
        elif event.key == "enter":
            self.dismiss(True)
