import cmd
from core.controllers import Supervisor
from core.models import User, Trip
from core.utils.cmd_utils import check_types, bcolors, errprint, succprint, warnprint, draw_table
from core.utils.parsers import parser_get_s, parser_insert_s, parser_update_m, parser_update_s, ParseException
from config import *

WRONG_USE = 'Wrong use.'


class CLIController(cmd.Cmd):
    prompt = bcolors.OKCYAN+'$ > '+bcolors.ENDC
    intro = bcolors.HEADER+bcolors.BOLD+"Hello! Welcome to CLI! For list of cmds, use `help`"+bcolors.ENDC*2

    def __init__(self, file_path):
        self.file_path = file_path
        self.supervisor = Supervisor(MASTER_STORAGE_FILE_NAME, User, MASTER_INDEX_FILE_NAME,
                                     SLAVE_STORAGE_FILENAME, Trip, SLAVE_JUNK_FILENAME, SLAVE_INDEX_FILENAME)
        cmd.Cmd.__init__(self)
        method_list = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('do_')]
        aliases = {}
        for method in method_list:
            aliases[method.replace('do_', '').replace('_', '-')] = getattr(self, method)

        self.aliases = aliases

    # For file input:

    # def cmdloop(self):
    #     try:
    #         with open(self.file_path, 'r') as file:
    #             for line in file:
    #                 line = line.strip()
    #                 if line and not line.startswith('#'):  # Ignore empty lines and comments
    #                     self.onecmd(line)
    #     except FileNotFoundError:
    #         print(f"Error: File '{self.file_path}' not found. ")
    #     except Exception as e:
    #         raise e

    def parseline(self, line):
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        # elif line[0] == '!':
        #     if hasattr(self, 'do_shell'):
        #         line = 'shell ' + line[1:]
        #     else:
        #         return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars+'-': i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def default(self, line):
        cmd, arg, line = self.parseline(line)
        if cmd in self.aliases:
            self.aliases[cmd](arg)
        else:
            errprint("*** Unknown syntax: %s\nTry `help`" % line)

    def do_insert_m(self, args):
        """Creates a new master object User:
        insert-m <user_id : int> <name: str> <username: str>"""
        check = check_types(args, [int, str, str])
        if check:
            if check[0] < 0:
                errprint(f'Id field must be >= 0')
                return
            master = User(uid=check[0], name=check[1], username=check[2])
            res = self.supervisor.insert_m(master)
            if res is not None:
                succprint(f'Inserted object User{check} @ {res}')
            else:
                errprint(f'MasterId {check[0]} is busy')

        else:
            errprint(WRONG_USE)
            warnprint('Info: ' + self.do_insert_m.__doc__)

    def do_insert_s(self, args):
        """Creates a new slave object Trip:
        insert-s -u <user_id: int> -t <trip_id: int> <trip_name: str> <trip_destination: str> <trip_days: int>"""
        try:
            namespace = parser_insert_s.parse_args(args.split())
            master_id = int(namespace.user[0])
            check = check_types(namespace.trip, [int, str, str, int], True)
            if check:
                if master_id < 0 or check[0] < 0:
                    errprint(f'Id field must be >= 0')
                    return
                slave = Trip(uid=check[0], name=check[1], destination=check[2], days_duration=check[3],
                             master_id=master_id)
                res = self.supervisor.insert_s(slave)
                if res == 1:
                    succprint(f'Inserted object Trip{check} @ {res} for User({master_id})')
                elif res == -2:
                    errprint(f'User object with id {master_id} does not exist')
                elif res == -1:
                    errprint(f'SlaveId {check[0]} is busy')
            else:
                raise ValueError

        except (ValueError, TypeError, ParseException):
            errprint(WRONG_USE)
            warnprint('Info: ' + self.do_insert_s.__doc__)

    def do_get_m(self, args):
        """Gets master object User:
        get-m <user_id: int>"""
        check = check_types(args, [int])
        if check:
            master_id = check[0]
            if master_id < 0:
                errprint(f'No User with id {master_id}')
            res = self.supervisor.get_m(master_id)
            if res:
                res.print_model()
            else:
                errprint(f'No User with id {master_id}')

        else:
            if args == '':
                self.do_ut_m(args)
            else:
                errprint(WRONG_USE)
                warnprint('Info: ' + self.do_get_m.__doc__)

    def do_get_s(self, args):
        """Gets slave object Trip:
        get-s [-i/--id trip_id: int] [-u/--user user_id: int]
        [-i/--id] and [-u/--user] are exclusive, please provide at only one of them
        With no arguments provided, program will return all records"""
        try:
            namespace = parser_get_s.parse_args(args.split())
            slave_id: str = namespace.id
            master_id: str = namespace.user
            if slave_id is None:
                if master_id is None:
                    res = self.supervisor.get_s_all()
                    if res:
                        draw_table(res)
                    else:
                        print('Empty...')
                else:
                    # Will call exception if master_id is not all digits
                    m_id = int(master_id[0])
                    if m_id < 0:
                        errprint(f'No User with id {m_id}')
                        return
                    res = self.supervisor.get_s_all_for_master(m_id)
                    if res is not None:
                        if not res:
                            print('Empty...')
                        else:
                            draw_table(res)
                    else:
                        errprint(f'No User with id {m_id}')

            else:
                # Will call exception if master_id is not all digits
                s_id = int(slave_id[0])
                if s_id < 0:
                    errprint(f'No Trip with id {s_id}')
                    return
                res = self.supervisor.get_s_one(s_id)
                if res is not None:
                    res.print_model()
                else:
                    errprint(f'No Trip with id {s_id}')

        except (ValueError, TypeError, ParseException):
            errprint(WRONG_USE)
            warnprint('Info: ' + self.do_get_s.__doc__)

    def do_del_m(self, args):
        """Deletes master object User:
        del-m <user_id>"""
        check = check_types(args, [int])
        if check:
            master_id = check[0]
            if master_id < 0:
                errprint(f'No User with id {master_id}')
                return
            res = self.supervisor.del_m(master_id)
            if res:
                succprint(f'Deleted User with id {master_id}')
            else:
                errprint(f'No User with id {master_id}')
        else:
            errprint(WRONG_USE)
            warnprint('Info: ' + self.do_del_m.__doc__)

    def do_del_s(self, args):
        """Deletes slave object Trip:
        del-s <trip_id>"""
        check = check_types(args, [int])
        if check:
            slave_id = check[0]
            if slave_id < 0:
                errprint(f'No Trip with id {slave_id}')
                return
            res = self.supervisor.del_s(slave_id)
            if res:
                succprint(f'Deleted Trip with id {slave_id}')
            else:
                errprint(f'No Trip with id {slave_id}')
        else:
            errprint(WRONG_USE)
            warnprint('Info: ' + self.do_del_s.__doc__)

    def do_update_m(self, args):
        """Updates master object User:
        update-m <user_id: int> [-n/--name new_name] [-usn/--username new_username]"""
        try:
            namespace = parser_update_m.parse_args(args.split())
            master_id = namespace.user[0]
            if master_id < 0:
                errprint(f'No User with id {master_id}')
                return
            name = namespace.name
            username = namespace.username
            if not name and not username:
                raise ValueError
            user: User = self.supervisor.get_m(master_id)
            if user:
                if name:
                    user.name = name
                if username:
                    user.username = username

                res = self.supervisor.update_m(user)
                if res:
                    succprint(f'Successfully updated User @ {master_id}')
                else:
                    errprint(f'No User with id {master_id} (???)')
            else:
                errprint(f'No User with id {master_id}')
        except ValueError:
            errprint('At least one of optional parameters is required. Use `help update_m`')
        except (TypeError, ParseException):
            errprint(WRONG_USE)
            warnprint('Info: ' + self.do_update_m.__doc__)

    def do_update_s(self, args):
        """Updates slave object Trip:
        update-s <trip_id: int> [-n/--name new_name] [-dest/--destination new_destin.] [-d/--days days_amount: int]"""
        try:
            namespace = parser_update_s.parse_args(args.split())
            slave_id = namespace.trip[0]
            if slave_id < 0:
                errprint(f'No Trip with id {slave_id}')
                return
            name = namespace.name
            destination = namespace.destination
            days = namespace.days
            if not name and not destination and not days:
                raise ValueError
            trip: Trip = self.supervisor.get_s_one(slave_id)
            if trip:
                if name:
                    trip.name = name
                if destination:
                    trip.destination = destination
                if days:
                    trip.days_duration = days

                res = self.supervisor.update_s(trip)
                if res:
                    succprint(f'Successfully updated Trip @ {slave_id}')
                else:
                    errprint(f'No User with id {slave_id} (???)')
            else:
                errprint(f'No User with id {slave_id}')

        except (ValueError, TypeError, ParseException):
            errprint(WRONG_USE)
            warnprint('Info: ' + self.do_update_s.__doc__)

    def do_ut_m(self, args):
        res = self.supervisor.ut_m()
        if res:
            draw_table(res)
        else:
            print('Empty.')

    def do_ut_s(self, args):
        res = self.supervisor.ut_s()
        if res:
            draw_table(res)
        else:
            print('Empty.')

    def do_exit(self, arg):
        """Exit the program"""
        print("Exiting...")
        return True
