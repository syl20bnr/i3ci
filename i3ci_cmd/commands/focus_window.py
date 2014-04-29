import command
import i3_utils
from i3_action import Action


class focus_window(command.Command):
    ''' Focus the nth window of the current workspace.
     Only the first 10 windows can be focused [0, 9]. '''

    def init_parser(self, parser):
        parser.add_argument(
            'index',
            type=int,
            choices=range(0, 10),
            help=('Window index. The order depends on the layout tree so '
                  'there is no simple rule to know which index corresponds to '
                  'which window, but indexes are easy to guess for simple '
                  'layout trees. Beware, the first window (top left) is at '
                  'index 1 and the index 0 is the 10nth window.'))
        parser.add_argument(
            '-w', '--workspace',
            required=False,
            default=None,
            type=str,
            help=('A workspace name. If not specified then the current '
                  'workspace is selected.'))
        return self

    def validate_args(self, args):
        self._args = args
        return True

    def process(self):
        wins = i3_utils.get_windows_from_workspace(self._args.workspace)
        action = Action()
        nth = self._args.index
        if nth == 0:
            nth = 10
        action.add_action(Action.focus_window, (wins[nth-1],))
        action.process()
