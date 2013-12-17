#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci-menu: Returns the current workspace name.

import i3

import common
import cur_output


def get_prompt(output):
    prompt = "workspace"
    if output != 'all':
        prompt += " on {0}".format(output)
    return "Current {0} ->".format(prompt)


def get_current_workspace(output='all'):
    workspaces = i3.msg('get_workspaces')
    if output == 'all' or output == cur_output.feed():
        return i3.filter(tree=workspaces, focused=True)
    else:
        return i3.filter(tree=workspaces, output=output, visible=True)


def feed(output='all'):
    ''' Returns the current workspace on the specified output '''
    workspace = get_current_workspace(output)
    if workspace:
        return workspace[0]['name']
    return ''


if __name__ == '__main__':
    import argparse
    PARSER = argparse.ArgumentParser(prog='cur_workspace')
    common.add_monitor_param(PARSER)
    args = PARSER.parse_args()
    mon = common.get_monitor_value(args)
    print('\n'.join(feed(mon)))
