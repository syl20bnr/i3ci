#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci-menu: Returns to stdout the list of all current windows,
# the output can be filtered by windows instance name and output.
import re

from Xlib import display
import i3

import common
import workspaces


def get_prompt(verb, win_inst=None, output='all'):
    prompt = "window"
    if win_inst:
        prompt = win_inst
    if output != 'all':
        m = common.get_natural_monitor_value(output)
        prompt += " on {0}".format(m)
    return "{0} {1} ->".format(verb, prompt)


def get_windows(win_inst=None, output='all'):
    ''' Returns a dictionary of key-value pairs of a window text and window id.
    Each window text is of format "[instance] window title (instance number)"
    '''
    dpy = display.Display()
    res = {}
    lmax = 0
    for ws in workspaces.get_workspaces_no_prefix():
        workspace = i3.filter(name=ws)
        if not workspace:
            continue
        workspace = workspace[0]
        wname = workspace['name']
        windows = i3.filter(workspace, nodes=[])
        instances = {}
        # adds windows and their ids to the clients dictionary
        for window in windows:
            if window['window'] is None:
                continue
            xwin = dpy.create_resource_object('window', window['window'])
            inst, _ = xwin.get_wm_class()
            if inst:
                eligible = win_inst is None or win_inst == inst
                if eligible and output != 'all':
                    # list only the windows on the specified output
                    id_ = window['id']
                    tree = i3.filter(name=output)
                    eligible = i3.filter(tree, id=id_)
                if eligible:
                    win = window['name']
                    if win_inst:
                        win = u'({0}) {1}'.format(wname, win)
                    else:
                        if len(inst) + 2 > lmax:
                            lmax = len(inst) + 2
                        win = u'({0}) [{1}] {2}'.format(wname, inst, win)
                    # appends an instance number if other instances are present
                    if win in instances:
                        instances[win] += 1
                        win = '%s (%d)' % (win, instances[win])
                    else:
                        instances[win] = 1
                    res[win] = window['id']
    if lmax:
        res = _format_dict(res, lmax)
    return res


def feed(win_inst=None, output='all'):
    ''' Returns a tuple (l, d) where l is a sorted list of windows and d the
    dictionary to map their ID.'''
    windows = get_windows(win_inst, output)
    return (sorted(windows.keys()), windows)


def _format_dict(d, lmax):
    ''' Align the window names. '''
    res = {}
    r = re.compile(r'(.*?)(\[.*?\])(.*)$')
    for k, v in d.iteritems():
        m = re.match(r, k)
        padding = lmax - len(m.group(2))
        if padding > 0:
            k = r.sub(r'\1\2' + ' '*padding + r'\3', k)
        res[k] = v
    return res


if __name__ == '__main__':
    import argparse
    PARSER = argparse.ArgumentParser(prog='windows')
    common.add_monitor_param(PARSER)
    PARSER.add_argument('-i', '--instance',
                        default=None,
                        help='X window instance name.')
    args = PARSER.parse_args()
    mon = common.get_monitor_value(args)
    print('\n'.join(feed(args.instance, mon)[0]))
