import command
from start_application import start_application


class menu(command.Category):
    ''' Commands requiring the i3ci menu. To get the list of possible
    action type "i3ci_cmd menu -h" '''

    def get_subcommands(self):
        return [start_application]
