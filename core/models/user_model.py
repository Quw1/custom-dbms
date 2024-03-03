from .base_models import BaseMasterObject
from dataclasses import dataclass, field
import struct


@dataclass
class User(BaseMasterObject):
    name: str = ''
    username: str = ''

    uid: int = -1
    first_slave_node: int = -1
    last_slave_node: int = -1
    _fmt: str = field(init=False, repr=False, default='<i25s20sii')

    def to_bytes(self):
        return struct.pack(
            self._fmt, self.uid, self.name.encode(), self.username.encode(),
            self.first_slave_node, self.last_slave_node
        )

    def from_bytes(self, bin_data):
        uid, name, username, first_slave_node, last_slave_node = struct.unpack(self._fmt, bin_data)
        self.uid = uid
        self.name = name.rstrip(b'\x00').decode()
        self.username = username.rstrip(b'\x00').decode()
        self.first_slave_node = first_slave_node
        self.last_slave_node = last_slave_node
        return self
