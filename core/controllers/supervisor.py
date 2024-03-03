from .driver_config import META_TYPE, BaseMasterObject, BaseSlaveObject
from .managers import MasterManager, SlaveManager


class Supervisor:
    def __init__(self, master_filename: str,
                 master_object_type: META_TYPE,
                 master_index_filename: str,
                 slave_filename: str,
                 slave_object_type: META_TYPE,
                 slave_junk_filename: str,
                 slave_index_filename: str):

        self.master_manager = MasterManager(master_filename, master_object_type, master_index_filename)
        self.slave_manager = SlaveManager(slave_filename, slave_object_type, slave_junk_filename, slave_index_filename)

    def ut_m(self):
        return self.master_manager.read_all()

    def ut_s(self):
        return self.slave_manager.read_all()

    def get_m(self, master_id: int):
        return self.master_manager.get_one(master_id)

    def get_s_one(self, slave_id: int):
        return self.slave_manager.get_one(slave_id)

    def get_s_all_for_master(self, master_id: int):
        res = self.master_manager.get_one(master_id)
        if res is None:
            return None
        return self.slave_manager.get_all_linked(res.first_slave_node)

    def get_s_all(self):
        return self.slave_manager.get_all()

    def del_m(self, master_id: int):
        master = self.master_manager.get_one(master_id)
        if master:
            first_slave = master.first_slave_node
            if first_slave != -1:
                self.slave_manager.delete_all_linked(first_slave)
            self.master_manager.delete(master_id)

            if self.slave_manager.need_memory_fragmentation():
                self.optimise_memory()
            return True
        return False

    def del_s(self, slave_id: int):
        res = self.slave_manager.delete(slave_id)
        if res is not None:
            slave, address = res
            deleted_refs = self.master_manager.update_after_slave_del(slave.master_id, slave, address)
            if not deleted_refs:
                print('Unexpected situation in Supervisor.del_s :: deleted_refs == False')
            if self.slave_manager.need_memory_fragmentation():
                self.optimise_memory()
        return res

    def update_m(self, master_obj: BaseMasterObject):
        return self.master_manager.update(master_obj)

    def update_s(self, slave_obj: BaseSlaveObject):
        return self.slave_manager.update(slave_obj)

    def insert_m(self, master_obj):
        return self.master_manager.insert(master_obj)

    def insert_s(self, slave_obj: BaseSlaveObject) -> int:
        master_id = slave_obj.master_id
        master_obj = self.master_manager.get_one(master_id)
        if master_obj:
            slave_pos = self.slave_manager.insert(slave_obj, master_obj.last_slave_node)
            if slave_pos is not None:
                if master_obj.first_slave_node == -1:
                    master_obj.first_slave_node = slave_pos
                master_obj.last_slave_node = slave_pos
                self.master_manager.update(master_obj)
            else:
                return -1
            return 1
        else:
            return -2

    def optimise_memory(self):
        sorted_ind, sorted_junk = self.slave_manager.prepare_to_optimise()

        n = 0
        deleted_junk = []
        while n < min(len(sorted_junk), len(sorted_ind)):
            if sorted_junk[n].address < sorted_ind[n].address:
                old_addr = sorted_ind[n].address
                new_addr = sorted_junk[n].address

                temp = self.slave_manager.move(old_addr, new_addr)
                self.master_manager.update_after_slave_move(temp.master_id, old_addr, new_addr)

                sorted_ind[n].address = new_addr
                deleted_junk.append(sorted_junk[n])
            else:
                break
            n += 1

        sorted_junk = [i for i in sorted_junk if i not in deleted_junk]

        self.slave_manager.finish_optimising(sorted_ind, sorted_junk)
        