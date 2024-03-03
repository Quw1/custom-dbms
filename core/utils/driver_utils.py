from core.models import Index, Junk


def key_sort_by_address(data: Index | Junk):
    return data.address


def key_sort_by_obj_id(data: Index):
    return data.obj_id