from core.controllers.base import BaseManager, BaseFileRAMDriver
from core.controllers.driver_config import META_TYPE, BaseSlaveObject, Index, Junk, MEMORY_FRAG_THRESHOLD
from core.utils.driver_utils import key_sort_by_address


class SlaveManager(BaseManager):

    def __init__(self, slave_filename: str,
                 slave_object_type: META_TYPE,
                 slave_junk_filename: str,
                 slave_index_filename: str,
                 ):
        super().__init__(slave_filename,
                         slave_object_type,
                         slave_index_filename,
                         )

        self._junk_manager = self.JunkManager(slave_junk_filename)

    # Junk manager for SlaveManager
    class JunkManager(BaseFileRAMDriver):

        def __init__(self, filename):
            super().__init__(filename, Junk)
            self.junk: list[Junk] = self.data

        def __del__(self):
            super().set_data(data=self.junk)
            super().__del__()

    def _set_next_ref(self, record_pos: int, next_record_pos: int) -> None:

        res = self._read(position=record_pos)
        res.next_node = next_record_pos
        self._write(res, record_pos)

    def _add_node(self, obj: BaseSlaveObject, record_pos: int, prev_record_pos: int = -1, mode: int = 0) -> None:

        obj.prev_node = prev_record_pos
        self._write(obj, record_pos, mode)

        if prev_record_pos != -1:
            self._set_next_ref(prev_record_pos, record_pos)

    def insert(self, obj: BaseSlaveObject, prev_record_pos: int):

        obj_id = obj.uid
        if self._get_index_if_exists(obj_id):
            return None

        if self._junk_manager.junk:
            write_pos = self._junk_manager.junk[0].address
            self._junk_manager.junk.pop(0)
        else:
            write_pos = self._get_cursor_info(0, 2)

        self._add_node(obj, write_pos, prev_record_pos, mode=0)

        new_index = Index(obj_id=obj_id, address=write_pos)
        self._index_manager.index.append(new_index)
        return write_pos

    def get_all_linked(self, first_node):

        linked_list = []
        read_pos = first_node
        while read_pos != -1:
            res = self._read(read_pos)
            read_pos = res.next_node
            linked_list.append(res)
        return linked_list

    def delete(self, obj_id) -> tuple[BaseSlaveObject, int] | None:

        res = self._get_index_if_exists(obj_id)
        if res:
            obj = self._delete_node(res.address)
            self._update_node_ref_on_delete(obj.prev_node, obj.next_node)
            self._index_manager.index.remove(res)
            return obj, res.address
        return None

    def _update_node_ref(self, prev_node_pos, next_node_pos, new_pos_for_prev, new_pos_for_next):

        if prev_node_pos != -1:
            prev_obj = self._read(prev_node_pos)
            prev_obj.next_node = new_pos_for_prev
            self.update(prev_obj)
        if next_node_pos != -1:
            next_obj = self._read(next_node_pos)
            next_obj.prev_node = new_pos_for_next
            self.update(next_obj)

    def _update_node_ref_on_move(self, prev_node_pos, next_node_pos, new_pos):

        self._update_node_ref(prev_node_pos, next_node_pos, new_pos, new_pos)

    def _update_node_ref_on_delete(self, prev_node_pos, next_node_pos):

        self._update_node_ref(prev_node_pos, next_node_pos, next_node_pos, prev_node_pos)

    def _delete_node(self, obj_pos):

        obj = self._read(obj_pos)
        deleted_obj = self._Meta()
        deleted_obj.uid = obj.uid
        deleted_obj.exists = False
        new_junk = Junk(address=obj_pos)
        self._junk_manager.junk.append(new_junk)
        self._write(deleted_obj, obj_pos)
        return obj

    def delete_all_linked(self, first_slave_pos):

        deleted_ids = []
        read_pos = first_slave_pos
        while read_pos != -1:
            res = self._delete_node(read_pos)
            deleted_ids.append(res.uid)
            read_pos = res.next_node
        self._index_manager.index = [ind for ind in self._index_manager.index if ind.obj_id not in deleted_ids]

    def prepare_to_optimise(self):

        sorted_ind = sorted(self._index_manager.index, key=key_sort_by_address)
        sorted_junk = sorted(self._junk_manager.junk, key=key_sort_by_address)
        junk_len = len(sorted_junk)
        ind_len = len(sorted_ind)
        if ind_len == 0 or junk_len == 0:
            return False

        last_el = sorted_ind[-1]
        file_end = last_el.address + self._obj_size
        self._file_instance.truncate(file_end)
        self._file_instance.flush()

        remove_junk = []
        for junk in reversed(sorted_junk):
            if junk.address > file_end:
                remove_junk.append(junk)
        sorted_junk = [i for i in sorted_junk if i not in remove_junk]

        sorted_ind.reverse()
        return sorted_ind, sorted_junk
        ###

    def finish_optimising(self, sorted_ind, sorted_junk):
        ###
        sorted_ind.sort(key=key_sort_by_address)
        sorted_junk.sort(key=key_sort_by_address)

        last_el = sorted_ind[-1]
        file_end = last_el.address + self._obj_size
        self._file_instance.truncate(file_end)
        self._file_instance.flush()

        self._index_manager.index = sorted_ind
        self._junk_manager.junk = sorted_junk

    def need_memory_fragmentation(self):
        j_len = len(self._junk_manager.junk)
        i_len = len(self._index_manager.index)
        if i_len == 0 or j_len == 0:
            if i_len == 0:
                self._file_instance.truncate(0)
                self._file_instance.flush()
                self._junk_manager.junk = []
            return False
        if j_len / (j_len + i_len) >= MEMORY_FRAG_THRESHOLD:
            return True
        return False

    def move(self, old_pos, new_pos):
        res = self._read(old_pos)
        self._write(res, new_pos)
        self._update_node_ref_on_move(res.prev_node, res.next_node, new_pos)
        return res
