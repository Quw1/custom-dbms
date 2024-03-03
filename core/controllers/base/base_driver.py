from core.controllers.driver_config import META_TYPE, OBJ_TYPE, LIST_OBJ_TYPE
import os


class BaseDriver:

    def __init__(self, filename: str, meta: META_TYPE):
        if not os.path.exists(filename):
            with open(filename, 'w'):
                pass

        self._file_instance = open(filename, "r+b")
        self._obj_size = meta.get_size()
        self._Meta = meta

    def __del__(self):
        self._file_instance.close()

    def __check_meta(self, obj):

        if type(obj) is not self._Meta:
            raise TypeError('Object type is different from Meta type')

    def _write(self, obj: OBJ_TYPE, position: int = 0, mode: int = 0) -> None:

        try:
            self.__check_meta(obj)
            self._repos_cursor(position, mode)
            self._file_instance.write(obj.to_bytes())
            self._file_instance.flush()

        except Exception as e:
            raise Exception(f'Something went wrong in {self.__class__.__name__} ~ Driver.write :: {e}')

    def _read(self, position: int = 0) -> OBJ_TYPE:

        try:
            self._repos_cursor(position)
            res = self._file_instance.read(self._obj_size)
            temp = self._Meta()
            return temp.from_bytes(res)

        except Exception as e:
            raise Exception(f'Something went wrong in {self.__class__.__name__} ~ Driver.read :: {e}, {type(e)}')

    def read_all(self) -> LIST_OBJ_TYPE:

        try:
            self._repos_cursor()
            results = []
            while True:
                res = self._file_instance.read(self._Meta.get_size())
                if not res:
                    break
                temp = self._Meta()
                temp.from_bytes(res)
                results.append(temp)
            return results

        except Exception as e:
            raise Exception(f'Something went wrong in {self.__class__.__name__} ~ Driver.read_all :: {e}')

    def _write_all(self, obj: LIST_OBJ_TYPE) -> None:

        try:
            self.__check_meta(obj[0])
            for count, i in enumerate(obj):
                self._write(i, count * self._obj_size)

            # 3 elements: |[0-20] [20-40] [40-60]| <- 60 is file end
            new_file_end = self._obj_size * len(obj)
            self._file_instance.truncate(new_file_end)
            self._file_instance.flush()
        except Exception as e:
            raise Exception(f'Something went wrong in {self.__class__.__name__} ~ Driver.write_index :: {e}')

    def _get_cursor_info(self, pos: int = 0, mode: int = 0) -> int:
        self._repos_cursor(pos, mode)
        return self._file_instance.tell()

    def _repos_cursor(self, pos: int = 0, mode: int = 0) -> None:
        self._file_instance.seek(pos, mode)
