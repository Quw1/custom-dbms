from abc import ABCMeta
from . import BaseObject


class BaseSlaveObject(BaseObject, metaclass=ABCMeta):
    uid: int
    exists: bool
    next_node: int
    prev_node: int
    master_id: int
