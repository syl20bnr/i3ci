import command
from current_output import current_output
from current_workspace import current_workspace


class info(command.Category):
    ''' Get information. To get the list of the available commands type
    "i3ci_cmd info -h" '''

    def get_subcommands(self):
        return [current_output,
                current_workspace]
