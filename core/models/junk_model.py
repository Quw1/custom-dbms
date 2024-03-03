from .base_models import BaseObject
from dataclasses import dataclass, field
import struct


@dataclass
class Junk(BaseObject):
    address: int = -1
    _fmt: str = field(init=False, repr=False, default='<i')

    def to_bytes(self):
        return struct.pack(self._fmt, self.address)

    def from_bytes(self, bin_data):
        address, = struct.unpack(self._fmt, bin_data)
        self.address = address
        return self
