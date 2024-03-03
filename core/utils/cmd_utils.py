from prettytable import PrettyTable


def check_types(args, types, is_dict: bool = False):
    if is_dict:
        arg = args
    else:
        arg = args.split()
    res = []
    success = 1
    if len(arg) == len(types):
        for i, a in enumerate(arg):
            try:
                new_arg = types[i](a)
                res.append(new_arg)
            except Exception as e:
                success = 0
    else:
        success = 0

    if success:
        return res
    return False


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def errprint(message):
    print(bcolors.FAIL + message + bcolors.ENDC)


def succprint(message):
    print(bcolors.OKGREEN + message + bcolors.ENDC)


def infoprint(message):
    print(bcolors.OKBLUE + message + bcolors.ENDC)


def warnprint(message):
    print(bcolors.WARNING + message + bcolors.ENDC)


def draw_table(list_obj) -> None:
    table = PrettyTable()
    if not list_obj:
        pass
    else:
        table.field_names = [*vars(list_obj[0]).keys()]

        for obj in list_obj:
            table.add_row([*vars(obj).values()])
        print(table)
