from .base_models import BaseSlaveObject
from dataclasses import dataclass, field
import struct


@dataclass
class Trip(BaseSlaveObject):
    # Main fields
    name: str = ''
    destination: str = ''
    days_duration: int = 0
    # Service fields
    uid: int = -1
    exists: bool = True
    next_node: int = -1
    prev_node: int = -1
    master_id: int = -1
    _fmt: str = field(init=False, repr=False, default='<i25s20sH?iii')

    def to_bytes(self):
        return struct.pack(
            self._fmt, self.uid, self.name.encode(), self.destination.encode(), self.days_duration,
            self.exists, self.next_node, self.prev_node, self.master_id
        )

    def from_bytes(self, bin_data):
        uid, name, destination, days_duration, exists, next_node, prev_node, master_id \
            = struct.unpack(self._fmt, bin_data)
        self.uid = uid
        self.name = name.rstrip(b'\x00').decode()
        self.destination = destination.rstrip(b'\x00').decode()
        self.days_duration = days_duration
        self.exists = exists
        self.next_node = next_node
        self.prev_node = prev_node
        self.master_id = master_id
        return self
