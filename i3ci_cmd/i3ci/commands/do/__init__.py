'''
Perform a simple command. To get the list of possible action type
"i3ci_cmd do -h"
 '''
from i3ci import *


# Workspaces
# ----------------------------------------------------------------------------

class focus_active_workspace(command.Command):
    ''' Focus the active workspace on the specified monitor. '''

    def init_parser(self, parser):
        params.add_monitor_param(parser)
        return self

    def validate_args(self, args):
        self._mon = params.get_monitor_value(args)
        return True

    def process(self):
        wks = utils.get_current_workspace(self._mon)
        a = action.Action()
        a.add(action.Action.jump_to_workspace, (wks,))
        action.default_mode(a)
        a.process()


# Windows
# ----------------------------------------------------------------------------

class focus_window(command.Command):
    ''' Focus the nth window of the current workspace.
     Only the first 10 windows can be focused [0, 9]. '''

    def init_parser(self, parser):
        parser.add_argument(
            'index',
            type=int,
            choices=range(0, 10),
            help=('Window index. The order depends on the layout tree so '
                  'there is no simple rule to know which index corresponds '
                  'to which window, but indexes are easy to guess for simple '
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
        wins = utils.get_windows_from_workspace(self._args.workspace)
        a = action.Action()
        nth = self._args.index
        if nth == 0:
            nth = 10
        a.add(action.Action.focus_window, (wins[nth-1],))
        a.process()
