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

    def prepare_data(self, is_rtr: bool, datatype: str, value: str):
        if is_rtr:
            data = None
            dlc = 0
        if datatype == "float":
            data = bytearray(struct.pack("f", float(value)))
            dlc = 4
        elif datatype == "uint8_t":
            data = bytearray([int(value)])
            dlc = 1
        elif datatype == "bool":
            data = [1] if (value == True or value == "True") else [0]
            dlc = 1
        elif datatype == "uint16_t":
            data = bytearray(struct.pack("H", int(value)))
            dlc = 2
        elif datatype == "int16_t":
            data = bytearray(struct.pack("h", int(value)))
            dlc = 2
        elif datatype == "ulong64_t":
            data = bytearray(struct.pack("Q", int(value)))
            dlc = 8
        elif datatype == "string":
            data = bytearray(value, "utf-8")
            dlc = 8
        else:
            data = None
            dlc = 0
        return (data, dlc)

    def send(
        self, device_id, module_id, field_id, is_rtr=True, datatype=None, value=None
    ):
        assert 0 <= device_id < (1 << 4), "device_id must fit in 4 bits"
        assert 0 <= module_id < (1 << 4), "module_id must fit in 4 bits"
        assert 0 <= field_id < (1 << 3), "field_id must fit in 3 bits"

        identifier = (device_id << 7) | (module_id << 3) | field_id

        (data, dlc) = self.prepare_data(is_rtr, datatype, value)

        msg = can.Message(
            arbitration_id=identifier,
            data=data,
            dlc=dlc,
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
            if module_id not in self.modules:
                print("unknown module")
                return
            field = self.modules[module_id].fields[field_id]
            values = []

            remaining_data = msg.data

            datatypes = field.datatype.split(",")
            for datatype in datatypes:
                if datatype == "float":
                    data = remaining_data[:4]
                    remaining_data = remaining_data[4:]
                    value = round(struct.unpack("f", data)[0], 4)
                    values.append(value)
                elif datatype == "uint8_t":
                    data = remaining_data[:1]
                    remaining_data = remaining_data[1:]
                    values.append(data[0])
                elif datatype == "bool":
                    data = remaining_data[:1]
                    remaining_data = remaining_data[1:]
                    values.append(data[0] == 1)
                elif datatype == "uint16_t":
                    data = remaining_data[:2]
                    remaining_data = remaining_data[2:]
                    values.append(struct.unpack("H", data)[0])
                elif datatype == "int16_t":
                    data = remaining_data[:2]
                    remaining_data = remaining_data[2:]
                    values.append(struct.unpack("h", data)[0])
                elif datatype == "ulong64_t":
                    values.append(struct.unpack("Q", remaining_data)[0])
                elif datatype == "string":
                    values.append(
                        (struct.unpack(f"{msg.dlc}s", remaining_data)[0]).decode()
                    )
                else:
                    values.append(None)

            if len(values) == 1:
                values = values[0]

            event = SimpleCanEvent(msg, device_id, module_id, field_id, values)
            self.app.post_message(event)
