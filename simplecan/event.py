import can
from textual.message import Message


class SimpleCanEvent(Message):

    def __init__(
        self,
        msg: can.Message,
        device_id: int,
        module_id: int,
        field_id: int,
        value: any,
    ) -> None:
        self.msg = msg
        self.device_id = device_id
        self.module_id = module_id
        self.field_id = field_id
        self.value = value

        super().__init__()
