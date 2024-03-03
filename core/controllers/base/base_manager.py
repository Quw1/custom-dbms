from core.controllers.driver_config import META_TYPE, BaseSlaveObject, BaseMasterObject, Index
from . import BaseDriver
from . import BaseFileRAMDriver


class BaseManager(BaseDriver):

    def __init__(self, filename: str, meta: META_TYPE,
                 index_filename: str,
                 ):
        super().__init__(filename, meta)
        self._index_manager = self.IndexManager(index_filename)

    def _get_index_if_exists(self, obj_id):
        for ind in self._index_manager.index:
            if ind.obj_id == obj_id:
                return ind

        return None

    def update(self, new_obj: BaseMasterObject | BaseSlaveObject):

        obj_id = new_obj.uid
        res = self._get_index_if_exists(obj_id)
        if res:
            self._write(new_obj, res.address)
            return True
        else:
            return False

    def get_all(self) -> list[BaseSlaveObject | BaseMasterObject]:

        all_obj = []
        for i in self._index_manager.index:
            res = self._read(i.address)
            all_obj.append(res)
        return all_obj

    def get_one(self, obj_id: int) -> BaseSlaveObject | BaseMasterObject | None:

        res = self._get_index_if_exists(obj_id)
        if res:
            return self._read(res.address)
        return None

    # Index manager for BaseSupervisor
    class IndexManager(BaseFileRAMDriver):

        def __init__(self, filename):
            super().__init__(filename, Index)
            self.index: list[Index] = self.data

        def __del__(self):
            super().set_data(data=self.index)
            super().__del__()
