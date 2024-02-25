from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, OptionList, DataTable
from textual.containers import Vertical, Horizontal
from textual.widgets.option_list import Option
from textual import on
from threading import Lock
from widgets.can_footer import CanFooter
import struct
import can
from config import (
    load_config_from_yaml,
)
from can.interface import Bus

field_table_lock = Lock()
device_id = 0
can_footer = CanFooter()
config = load_config_from_yaml()
desired_connection = config.connection
available_connections = can.detect_available_configs()
is_available = any(
    (
        desired_connection["interface"] == connection["interface"]
        and desired_connection["channel"] == connection["channel"]
    )
    for connection in available_connections
)

if not is_available:
    print(f"Connection {desired_connection} is not available, have you started it?")
    exit(0)
else:
    print("Connection is available", type(desired_connection))

bus = can.Bus(**desired_connection)

modules = config.modules
module_options = [Option(val.name, id=key) for key, val in modules.items()]
module_list = OptionList(*module_options, name="modules")
field_table = DataTable()
field_table.cursor_type = "row"
selected_module_id = list(config.modules.keys())[0]


def send(device_id, module_id, field_id, is_rtr=True, data=None):
    assert 0 <= device_id < (1 << 4), "device_id must fit in 4 bits"
    assert 0 <= module_id < (1 << 4), "module_id must fit in 4 bits"
    assert 0 <= field_id < (1 << 3), "field_id must fit in 3 bits"

    identifier = (device_id << 7) | (module_id << 3) | field_id

    msg = can.Message(
        arbitration_id=identifier,
        data=None,
        dlc=0 if is_rtr else len(data),
        is_remote_frame=is_rtr,
        is_extended_id=False,
        is_error_frame=False,
        is_fd=False,
        is_rx=False,
        check=False,
    )
    bus.send(msg)


class VerticalLayoutExample(App):
    CSS_PATH = "main.css"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Header(),
            Horizontal(
                module_list,
                field_table,
                id="horizontal-layout",
            ),
            can_footer,
            id="vertical-layout",
        )

    def request_fields(self):
        mod = modules[selected_module_id]
        for field_id, _ in mod.fields.items():
            send(device_id, selected_module_id, field_id)

    def update_fields(self):
        # can_footer.on_can_message()
        mod = modules[selected_module_id]
        with field_table_lock:
            field_table.clear()
            for key, row in mod.fields.items():
                field_table.add_row(*row.values(), key=str(key), label=f"{key:#03x}")

    def on_mount(self) -> None:
        self.title = "CAN Text UI"
        self.sub_title = "For cybergear"
        field_table.add_column("name", key="name")
        field_table.add_column("description", key="description")
        field_table.add_column("value", key="value")
        field_table.add_column("datatype", key="datatype")

        # field_table.add_columns(*("name", "description", "value", "datatype"))
        self.update_fields()
        self.request_fields()

    @on(OptionList.OptionSelected)
    def module_selected(self, event: Option) -> None:
        global selected_module_id
        selected_module_id = event.option_id
        self.update_fields()
        self.request_fields()

    @on(DataTable.RowSelected)
    def field_selected(self, event):
        selected_field_id = event.row_key.value
        send(device_id, selected_module_id, selected_field_id, is_rtr=True)


app = VerticalLayoutExample()


def receiveCan(msg: can.Message):
    if msg is not None and msg.is_rx:
        if msg.is_error_frame:
            print("error frame")
        else:
            print(msg)
            device_id = (msg.arbitration_id >> 7) & 0b1111
            module_id = (msg.arbitration_id >> 3) & 0b1111
            field_id = msg.arbitration_id & 0b111

            field = modules[module_id].fields[field_id]
            if field.datatype == "float":
                data = struct.unpack("f", msg.data)[0]
            elif field.datatype == "byte":
                data = msg.data[0]
            elif field.datatype == "uint16_t":
                data = struct.unpack("H", msg.data)[0]
            field.value = data
            # if field_id in field_table._row_locations:
            # row = field_table.get_row(field_id)
            # col = field_table.get_column(str(2))
            field_table.update_cell(
                row_key=str(field_id), column_key="value", value=data
            )


can.Notifier(bus, listeners=[receiveCan, can_footer.on_can_message])

bus.flush_tx_buffer()

if __name__ == "__main__":
    app._closing
    app.run()
