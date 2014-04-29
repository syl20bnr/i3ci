import command
from focus_window import focus_window
from focus_active_workspace import focus_active_workspace


class do(command.Category):
    ''' Perform a simple command. To get the list of possible action type
    "i3ci_cmd do -h" '''

    def get_subcommands(self):
        return [focus_window,
                focus_active_workspace]
