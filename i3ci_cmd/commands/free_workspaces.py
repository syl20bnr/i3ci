import i3_utils
import command


class free_workspaces(command.Command):
    ''' Output free workspace names from the catalog. '''

    def process(self):
        print i3_utils.get_free_workspaces()
