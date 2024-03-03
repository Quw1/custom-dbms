from core.controllers.base import BaseManager
from core.controllers.driver_config import META_TYPE, BaseMasterObject, BaseSlaveObject, Index


class MasterManager(BaseManager):

    def __init__(self, master_filename: str,
                 master_object_type: META_TYPE,
                 master_index_filename: str,
                 ):
        super().__init__(master_filename,
                         master_object_type,
                         master_index_filename,
                         )

    def insert(self, obj: BaseMasterObject):

        obj_id = obj.uid
        check = self._get_index_if_exists(obj_id)
        if check:
            return None

        write_pos = self._get_cursor_info(0, 2)
        new_index = Index(obj_id=obj_id, address=write_pos)
        self._write(obj, write_pos)
        self._index_manager.index.append(new_index)
        return write_pos

    def delete(self, obj_id: int):

        ind = self._get_index_if_exists(obj_id)
        if ind:
            self._delete_node(ind.address)
            self._index_manager.index.remove(ind)
            return True
        else:
            return False

    def _delete_node(self, obj_position: int):

        file_len = self._get_cursor_info(0, 2)
        last_el_pos = file_len - self._obj_size

        if obj_position != last_el_pos:
            last_el = self._read(last_el_pos)
            self._write(last_el, obj_position)
            for n, ind in enumerate(self._index_manager.index):
                if ind.obj_id == last_el.uid:
                    self._index_manager.index[n].address = obj_position

        self._file_instance.truncate(file_len - self._obj_size)
        self._file_instance.flush()

    def _update_slave_refs(self, master_id: int, first_slave_pos_old, first_slave_pos_new,
                           last_slave_pos_old, last_slave_pos_new):

        master = self.get_one(master_id)
        if master is not None:
            to_update = False

            if master.first_slave_node == first_slave_pos_old:
                to_update = True
                master.first_slave_node = first_slave_pos_new

            if master.last_slave_node == last_slave_pos_old:
                to_update = True
                master.last_slave_node = last_slave_pos_new

            if to_update:
                self.update(master)

            return True
        else:
            return False

    def update_after_slave_del(self, master_id: int, slave_obj: BaseSlaveObject, slave_address: int):

        return self._update_slave_refs(master_id, slave_address, slave_obj.next_node,
                                       slave_address, slave_obj.prev_node)

    def update_after_slave_move(self, master_id, old_slave_pos, new_slave_pos):

        return self._update_slave_refs(master_id, old_slave_pos, new_slave_pos, old_slave_pos, new_slave_pos)

    # not used
    def ut_m(self) -> None:
        try:
            self._repos_cursor()
            results = []
            while True:
                pos = self._get_cursor_info()
                res = self._file_instance.read(self._Meta.get_size())
                if not res:
                    break
                temp = self._Meta()
                temp.from_bytes(res)
                results.append([pos, temp])
            print(results)

        except Exception as e:
            raise Exception(f'Something went wrong in {self.__class__.__name__} ~ Driver.read_all :: {e}')
