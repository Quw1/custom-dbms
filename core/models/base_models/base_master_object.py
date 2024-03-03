from abc import ABCMeta
from . import BaseObject


class BaseMasterObject(BaseObject, metaclass=ABCMeta):
    uid: int
    first_slave_node: int
    last_slave_node: int