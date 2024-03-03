from . import BaseDriver
from core.controllers.driver_config import Type, Index, Junk


class BaseFileRAMDriver(BaseDriver):

    def __init__(self, filename, meta: Type[Index | Junk]):
        super().__init__(filename, meta)
        self.data: list[Index | Junk] = self.read_all()

    def set_data(self, data: list[Index | Junk]):
        self.data = data

    def __del__(self):
        if self.data:
            self._write_all(self.data)
        else:
            self._file_instance.truncate(0)
            self._file_instance.flush()
        super().__del__()
