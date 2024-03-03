from abc import ABC, abstractmethod
from dataclasses import dataclass
import struct
from core.utils.cmd_utils import draw_table


@dataclass
class BaseObject(ABC):
    _fmt: str

    @abstractmethod
    def to_bytes(self):
        pass

    @abstractmethod
    def from_bytes(self, bin_data):
        pass

    @classmethod
    def get_size(cls):
        return struct.Struct(cls._fmt).size

    def print_model(self):
        draw_table([self])
