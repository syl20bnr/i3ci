import i3_utils
import command


class current_output(command.Command):
    ''' Output the name of the current output. '''

    def process(self):
        print i3_utils.get_current_output()
