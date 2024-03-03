from typing import Type
from core.models import Junk, Index
from core.models.base_models import BaseMasterObject, BaseSlaveObject


LIST_OBJ_TYPE = list[BaseSlaveObject] | list[BaseMasterObject] | list[Junk] | list[Index]
META_TYPE = Type[BaseSlaveObject | BaseMasterObject | Junk | Index]
OBJ_TYPE = BaseSlaveObject | BaseMasterObject | Junk | Index
MNG_OBJ_TYPE = BaseSlaveObject | BaseMasterObject

MEMORY_FRAG_THRESHOLD = 0.3
