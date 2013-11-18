#!/usr/bin/env python

# author: syl20bnr (2013)
# goal: i3 actions module.

import os
from subprocess import Popen, PIPE

import i3
from Xlib import display

import dmenu
from constants import DMENU_MAX_ROW, DMENU_FONT, DMENU_HEIGHT
from feeders import (cur_workspace,
                     cur_workspaces,
                     free_workspaces,
                     cur_output)


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
# DMENU = os.path.normpath(os.path.join(MODULE_PATH, '../../bin/dmenu'))


class Action(object):
    ''' Define an i3-msg action. '''

    def __init__(self):
        self._actions = []

    def add_action(self, action, args=None):
        if args:
            action = action.__call__(self, *args)
        else:
            action = action.__call__(self)
        self._actions.append(action)

    def get_command(self):
        return 'i3-msg ' + ','.join(self._actions)

    def process(self):
        Popen(self.get_command(), shell=True)

    def exec_(self, app):
        return 'exec {0}'.format(app)

    def set_mode(self, mode):
        ''' Set the specified mode '''
        return 'mode {0}'.format(mode)

    def set_default_mode(self):
        ''' Set the default mode '''
        return self.set_mode('default')

    def jump_to_window(self, window):
        ''' Jump to the specified window. '''
        return '[con_id={0}] focus'.format(window)

    def jump_to_workspace(self, workspace):
        ''' Jump to the given workspace.
        Current used workspaces are prefixed with a dot '.'
        Workspace '`' means "back_and_forth" command.
        Workspace '=' is the scratch pad
        '''
        if workspace == '`':
            return "workspace back_and_forth"
        elif workspace == '=':
            return "scratchpad show"
        else:
            return "workspace {0}".format(workspace)

    def send_window_to_output(self, output):
        ''' Send the current window to the specified output. '''
        return "move to output {0}".format(output)

    def send_workspace_to_output(self, output):
        ''' Send the current workspace to the specified output. '''
        return "move workspace to output {0}".format(output)

    def send_window_to_workspace(self, workspace):
        ''' Send the current window to the passed workspace. '''
        if workspace == '`':
            return "move workspace back_and_forth"
        elif workspace == '=':
            return "move scratchpad"
        else:
            return "move workspace {0}".format(workspace)

    def focus_output(self, output):
        ''' Focus the specified output. '''
        return "focus output {0}".format(output)

    def focus_window(self, id_):
        ''' Focus the specified output. '''
        return "[con_id={0}] focus".format(id_)

    def mark_window(self, id_, mark):
        ''' Set the passed mark to the window with the passed id_.  '''
        return '[con_id={0}] mark {1}'.format(id_, mark)

    def unmark_window(self, mark):
        ''' Disable the passed mark.  '''
        return 'unmark {0}'.format(mark)

    def rename_workspace(self, from_, to):
        ''' Rename the workspace '''
        return '\'rename workspace "{0}" to "{1}"\''.format(from_, to)

    def cmd(self, cmd):
        # wonderful method :-)
        return cmd


# ----------------------------------------------------------------------------
#  Action groups
# ----------------------------------------------------------------------------


def default_mode(action=None):
    ''' Add or perform an action to set the default mode. '''
    if action:
        action.add_action(Action.set_default_mode)
    else:
        action = Action()
        action.add_action(Action.set_default_mode)
        action.process()


def get_max_row(rcount):
    return max([0, min([DMENU_MAX_ROW, rcount])])


def launch_app(feeder, app=None, output='all', free=False):
    ''' Launch an application on the specified monitor.
    output='all' means the current workspace on the current monitor.
    If free is true then the application is opened in a new workspace.
    '''
    reply = app
    if not reply:
        input_ = feeder.feed().encode('utf-8')
        size = get_max_row(len(input_))
        proc = dmenu.call(lmax=size,
                          f=DMENU_FONT,
                          h=DMENU_HEIGHT)
        reply = proc.communicate(input_)[0]
    if reply:
        reply = reply.decode('utf-8')
        if '-cd' in reply:
            # MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
            # DMENU = os.path.normpath(os.path.join(MODULE_PATH,
            # '../../bin/dmenu'))
            xcwd = Popen('xcwd', stdin=PIPE, stdout=PIPE).communicate()[0]
            reply = '"' + reply + ' ' + xcwd + '"'
        if not free and (output == 'all' or
                         output == cur_output.get_current_output()):
            # open on the current workspace
            action = Action()
            action.add_action(Action.exec_, (reply,))
            default_mode(action)
            action.process()
        if not free and (output != 'all' and
                         output != cur_output.get_current_output()):
            # open on the visible workspace on another output
            otherw = cur_workspace.feed(output)
            action = Action()
            action.add_action(Action.jump_to_workspace, (otherw,))
            action.add_action(Action.exec_, (reply,))
            default_mode(action)
            action.process()
        elif free and (output == 'all' or
                       output == cur_output.get_current_output()):
            # free workspace on the current output
            freew = free_workspaces.get_free_workspaces()[0]
            action = Action()
            action.add_action(Action.jump_to_workspace, (freew,))
            action.add_action(Action.exec_, (reply,))
            default_mode(action)
            action.process()
        elif free and (output != 'all' and
                       output != cur_output.get_current_output()):
            # free workspace on another output
            freew = free_workspaces.get_free_workspaces()[0]
            action = Action()
            action.add_action(Action.focus_output, (output,))
            action.add_action(Action.jump_to_workspace, (freew,))
            action.add_action(Action.exec_, (reply,))
            default_mode(action)
            action.process()
    else:
        default_mode()


def clone_window(output='all', free=False):
    from feeders import cur_window
    win = cur_window.get_current_window()[0]
    dpy = display.Display()
    xwin = dpy.create_resource_object('window', win['window'])
    inst, _ = xwin.get_wm_class()
    if inst:
        if inst == 'urxvt':
            inst += ' -cd'
        launch_app(None, inst, output, free)


def jump_to_window(feeder, inst, output='all'):
    ''' Jump to the window chosen by the user using dmenu. '''
    (wins, d) = feeder.feed(inst, output)
    size = get_max_row(len(wins))
    proc = dmenu.call(f=DMENU_FONT,
                      lmax=size,
                      sb='#b58900')
    reply = proc.communicate('\n'.join(wins).encode('utf-8'))[0]
    if reply:
        reply = reply.decode('utf-8')
        action = Action()
        action.add_action(Action.jump_to_window, (d.get(reply),))
        default_mode(action)
        action.process()
    else:
        default_mode()


def jump_to_workspace(feeder):
    ''' Jump to the workspace chosen by the user using dmenu. '''
    input_ = '\n'.join(feeder.feed()).encode('utf-8')
    size = get_max_row(len(input_))
    proc = dmenu.call(h=DMENU_HEIGHT,
                      lmax=size,
                      r=True,
                      sb='#d33682')
    reply = proc.communicate(input_)[0]
    if reply:
        reply = reply.decode('utf-8')
        action = Action()
        action.add_action(Action.jump_to_workspace, (reply,))
        default_mode(action)
        action.process()
    else:
        default_mode()


def jump_to_currently_used_workspace(feeder, output='all'):
    ''' Jump to a curently used workspace on the specified outputs
    and chosen by the user using dmenu.
    '''
    input_ = '\n'.join(feeder.feed(output)).encode('utf-8')
    size = get_max_row(len(input_))
    proc = dmenu.call(f=DMENU_FONT,
                      h=DMENU_HEIGHT,
                      lmax=size,
                      r=True,
                      sb='#268bd2')
    reply = proc.communicate(input_)[0]
    if reply:
        reply = reply.decode('utf-8')
        action = Action()
        action.add_action(Action.jump_to_workspace, (reply,))
        default_mode(action)
        print action.get_command()
        action.process()
    else:
        default_mode()


def send_workspace_to_output(feeder, output='all'):
    ''' Send the current workspace to the selected output. '''
    if output == 'all':
        # be sure that the workspace exists
        cur_wks = cur_workspace.get_current_workspace()
        if not cur_wks:
            return
        outs = feeder.get_outputs_dictionary()
        # remove the current output
        coutput = cur_output.get_current_output()
        fouts = [k for k, v in outs.iteritems() if v != coutput]
        input_ = '\n'.join(sorted(fouts)).encode('utf-8')
        size = get_max_row(len(input_))
        proc = dmenu.call(f=DMENU_FONT,
                          h=DMENU_HEIGHT,
                          lmax=size,
                          r=False,
                          sb='#268bd2')
        reply = proc.communicate(input_)[0]
        if reply:
            reply = reply.decode('utf-8')
            output = outs[reply]
    action = Action()
    action.add_action(Action.send_workspace_to_output, (output,))
    default_mode(action)
    action.process()


def send_window_to_output(feeder, output='all'):
    ''' Send the current window to the selected output. '''
    if output == 'all':
        outs = feeder.get_outputs_dictionary()
        # remove the current output
        coutput = cur_output.get_current_output()
        fouts = [k for k, v in outs.iteritems() if v != coutput]
        input_ = '\n'.join(sorted(fouts)).encode('utf-8')
        size = get_max_row(len(input_))
        proc = dmenu.call(f=DMENU_FONT,
                          h=DMENU_HEIGHT,
                          lmax=size,
                          r=False,
                          sb='#268bd2')
        reply = proc.communicate(input_)[0]
        if reply:
            reply = reply.decode('utf-8')
            output = outs[reply]
    action = Action()
    action.add_action(Action.send_window_to_output, (output,))
    action.add_action(Action.focus_output, (output,))
    default_mode(action)
    action.process()


def send_window_to_workspace(feeder):
    ''' Send the current window to the selected workspace. '''
    input_ = '\n'.join(feeder.feed()).encode('utf-8')
    size = get_max_row(len(input_))
    proc = dmenu.call(f=DMENU_FONT,
                      h=DMENU_HEIGHT,
                      lmax=size,
                      r=True,
                      sb='#6c71c4')
    reply = proc.communicate(input_)[0]
    if reply:
        reply = reply.decode('utf-8')
        action = Action()
        action.add_action(Action.send_window_to_workspace, (reply,))
        default_mode(action)
        action.process()
    else:
        default_mode()


def send_window_to_free_workspace(feeder, output):
    ''' Send the current window to a free workspace on the given output. '''
    freew = feeder.feed()
    if freew:
        from feeders import cur_output
        w = freew[0]
        action = Action()
        action.add_action(Action.send_window_to_workspace, (w,))
        action.add_action(Action.jump_to_workspace, (w,))
        if output != 'all' and output != cur_output.feed():
            action.add_action(Action.send_workspace_to_output, (output,))
        default_mode(action)
        action.process()
    else:
        default_mode()


def send_window_to_used_workspace(feeder, output):
    ''' Send the current window to a used workspace on the given output. '''
    input_ = '\n'.join(feeder.feed(output)).encode('utf-8')
    size = get_max_row(len(input_))
    proc = dmenu.call(f=DMENU_FONT,
                      h=DMENU_HEIGHT,
                      lmax=size,
                      r=True,
                      sb='#6c71c4')
    reply = proc.communicate(input_)[0]
    if reply:
        reply = reply.decode('utf-8')
        action = Action()
        action.add_action(Action.send_window_to_workspace, (reply,))
        action.add_action(Action.jump_to_workspace, (reply,))
        default_mode(action)
        action.process()
    else:
        default_mode()


def _choose_other_windows(feeder, output):
    '''
    Launch a dmenu instance to select a window which is not on the current
    worspace.
    Return a tuple composed of the window name and the window id.
    Return None if nothing has been selected.
    '''
    (wins, d) = feeder.feed(output=output)
    size = get_max_row(len(wins))
    proc = dmenu.call(f=DMENU_FONT,
                      lmax=size,
                      sb='#6c71c4')
    ws = cur_workspace.feed()
    excluded_wins = _get_window_ids_of_workspace(ws)
    if excluded_wins:
        # remove the wins of the current output from the list
        wins = [k for k, v in d.iteritems() if v not in excluded_wins]
    reply = proc.communicate('\n'.join(wins).encode('utf-8'))[0]
    if reply:
        return reply, d.get(reply)
    else:
        return None, None


def send_window_to_win_workspace(feeder, output='all'):
    ''' Send the current window to the workspace of the selected window. '''
    win, win_id = _choose_other_windows(feeder, output)
    if win:
        ws = _get_window_workspace(win_id)
        action = Action()
        action.add_action(Action.send_window_to_workspace, (ws,))
        action.add_action(Action.jump_to_workspace, (ws,))
        default_mode(action)
        action.process()
    else:
        default_mode()


def bring_window(feeder, output='all'):
    ''' Bring the chosen window to the current workspace. '''
    win, win_id = _choose_other_windows(feeder, output)
    if win:
        # TODO
        ws = cur_workspace.feed()
        other_ws = _get_window_workspace(win_id)
        action = Action()
        # switch focus to the window to bring
        action.add_action(Action.jump_to_workspace, (other_ws,))
        action.focus_window(win_id)
        # send the window to the original workspace
        action.add_action(Action.send_window_to_workspace, (ws,))
        action.add_action(Action.jump_to_workspace, (ws,))
        # make sure the new window is focused at the end
        action.focus_window(win_id)
        default_mode(action)
        action.process()
    else:
        default_mode()


def focus_workspace(mon):
    wks = cur_workspace.feed(mon)
    action = Action()
    action.add_action(Action.jump_to_workspace, (wks,))
    default_mode(action)
    action.process()


def focus_nth_window(nth, ws=None):
    ''' Roughly focus the nth window in the hierarchy (limited to 10 first) '''
    wins = _get_windows_from_workspace(ws)
    action = Action()
    if nth == 0:
        nth = 10
    action.add_action(Action.focus_window, (wins[nth-1],))
    action.process()


def logout():
    from feeders import logout as logout_feeder
    from feeders import confirm
    proc = dmenu.call(f=DMENU_FONT,
                      lmax=4,
                      nb='#002b36',
                      nf='#eee8dc',
                      sb='#cb4b16',
                      sf='#eee8d5')
    reply = proc.communicate(
        '\n'.join(logout_feeder.feed()).encode('utf-8'))[0]
    if reply:
        action = Action()
        action.add_action(Action.set_mode, ("confirm {0} ?".format(reply),))
        action.process()
        proc = dmenu.call(f=DMENU_FONT,
                          lmax=4,
                          nb='#002b36',
                          nf='#eee8dc',
                          sb='#cb4b16',
                          sf='#eee8d5')
        conf = proc.communicate('\n'.join(confirm.feed()).encode('utf-8'))[0]
        if conf == 'OK':
            action = Action()
            default_mode(action)
            action.process()
            exec_ = os.path.join(MODULE_PATH, 'i3-exit')
            cmd = '{0} --{1}'.format(exec_, reply)
            Popen(cmd, shell=True)
            return
    default_mode()


def execute_cmd(feeder, prefix):
    ''' Execute: i3-msg prefix *user_choice* '''
    proc = dmenu.call(p=feeder.get_prompt(prefix),
                      f=DMENU_FONT,
                      h=DMENU_HEIGHT,
                      sb='#cb4b16')
    reply = proc.communicate('\n'.join(feeder.feed(prefix)).encode('utf-8'))[0]
    if reply:
        reply = reply.decode('utf-8')
        cmd = reply
        if prefix:
            cmd = prefix + ' ' + cmd
        action = Action()
        action.add_action(Action.cmd, (cmd,))
        action.process()


def _get_window_workspace(win_id):
    cworkspaces = cur_workspaces.get_cur_workspaces()
    for ws in cworkspaces:
        ws_tree = i3.filter(name=ws)
        if i3.filter(tree=ws_tree, id=win_id):
            return ws
    return None


def _get_window_ids_of_workspace(ws):
    res = []
    wks = i3.filter(name=ws)
    wins = i3.filter(tree=wks, nodes=[])
    for w in wins:
        res.append(w['id'])
    return res


def _get_windows_from_workspace(ws):
    res = []
    if ws is None:
        ws = cur_workspace.feed()
    workspace = i3.filter(name=ws)
    if workspace:
        workspace = workspace[0]
        windows = i3.filter(workspace, nodes=[])
        for window in windows:
            res.append(window['id'])
    return res
