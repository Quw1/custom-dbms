import argparse


class ParseException(BaseException):
    """Raised while parsing"""
    pass


class ArgParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()

    def error(self, message):
        raise ParseException(message)


parser_get_s = ArgParser()
group = parser_get_s.add_mutually_exclusive_group()
group.add_argument('-i', '--id', nargs=1, required=False)
group.add_argument('-u', '--user', nargs=1, required=False)

parser_insert_s = ArgParser()
parser_insert_s.add_argument('-u', '--user', nargs=1, required=True)
parser_insert_s.add_argument('-t', '--trip', nargs=4, required=True)

parser_update_m = ArgParser()
parser_update_m.add_argument('user', nargs=1, type=int)
parser_update_m.add_argument('-n', '--name', nargs='?', required=False, type=str)
parser_update_m.add_argument('-usn', '--username', nargs='?', required=False, type=str)

parser_update_s = ArgParser()
parser_update_s.add_argument('trip', nargs=1, type=int)
parser_update_s.add_argument('-n', '--name', nargs='?', required=False, type=str)
parser_update_s.add_argument('-dest', '--destination', nargs='?', required=False, type=str)
parser_update_s.add_argument('-d', '--days', nargs='?', required=False, type=int)
