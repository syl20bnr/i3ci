#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for dmenu: Returns to stdout the list of all possible workspaces

import i3

import common
import outputs
import workspaces


def get_prompt(verb, output):
    prompt = "workspace"
    if output != 'all':
        m = common.get_natural_monitor_value(output)
        prompt += " on {0}".format(m)
    return "{0} current {1} ->".format(verb, prompt)


def get_cur_workspaces(output='all'):
    ''' Return a list of all currently used workspaces on the specified
    output.
    '''
    all_ws = workspaces.get_workspaces_no_prefix()
    used = []
    ws_tree = i3.msg('get_workspaces')
    outs = outputs.get_outputs_dictionary()
    for o in outs.itervalues():
        if output == 'all' or output == o:
            for ws in all_ws:
                if i3.filter(tree=ws_tree, output=o, name=ws):
                    used.append(ws)
    used.append('`')
    return sorted(used)


def feed(output='all'):
    ''' Return a list of all currently used workspaces on the specified
    output.
    '''
    res = get_cur_workspaces(output)
    return res


if __name__ == '__main__':
    import argparse
    PARSER = argparse.ArgumentParser(prog='cur_workspaces')
    common.add_monitor_param(PARSER)
    args = PARSER.parse_args()
    mon = common.get_monitor_value(args)
    print('\n'.join(feed(mon)))
