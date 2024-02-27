import can
import struct
from typing import Dict
from textual.app import App
from config.config import CanModule
from simplecan.event import SimpleCanEvent


class SimpleCanController:

    def __init__(
        self, app: App, connection_config: Dict, modules: Dict[int, CanModule]
    ):
        self.app = app
        self.modules = modules
        available_connections = can.detect_available_configs()
        is_available = any(
            (
                connection_config["interface"] == connection["interface"]
                and connection_config["channel"] == connection["channel"]
            )
            for connection in available_connections
        )

        if not is_available:
            print(
                f"Connection {connection_config} is not available, have you started it?"
            )
            exit(0)
        else:
            print("Connection is available", type(connection_config))

        self.bus = can.Bus(**connection_config)
        can.Notifier(
            self.bus, listeners=[self.receive_can]  # , self.can_footer.on_can_message]
        )  # , ])

        self.bus.flush_tx_buffer()

    def send(self, device_id, module_id, field_id, is_rtr=True, data=None):
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
        self.bus.send(msg)

    def receive_can(self, msg: can.Message):
        device_id = (msg.arbitration_id >> 7) & 0b1111
        module_id = (msg.arbitration_id >> 3) & 0b1111
        field_id = msg.arbitration_id & 0b111

        if msg.dlc > 0 and not msg.is_error_frame:
            field = self.modules[module_id].fields[field_id]

            if field.datatype == "float":
                value = struct.unpack("f", msg.data)[0]
            elif field.datatype == "byte":
                value = msg.data[0]
            elif field.datatype == "uint16_t":
                value = struct.unpack("H", msg.data)[0]
            else:
                value = None
        else:
            value = None

        event = SimpleCanEvent(msg, device_id, module_id, field_id, value)
        self.app.post_message(event)
