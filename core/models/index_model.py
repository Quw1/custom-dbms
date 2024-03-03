from .base_models import BaseObject
from dataclasses import dataclass, field
import struct


@dataclass
class Index(BaseObject):
    obj_id: int = -1
    address: int = -1
    _fmt: str = field(init=False, repr=False, default='<ii')

    def to_bytes(self):
        return struct.pack(self._fmt, self.obj_id, self.address)

    def from_bytes(self, bin_data):
        obj_id, address = struct.unpack(self._fmt, bin_data)
        self.obj_id = obj_id
        self.address = address
        return self

