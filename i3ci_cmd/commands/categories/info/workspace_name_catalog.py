import i3_utils
import command


class workspace_name_catalog(command.Command):
    ''' Return a list of all possible one char workspace names. '''

    def process(self):
        print i3_utils.get_workspace_name_catalog()
