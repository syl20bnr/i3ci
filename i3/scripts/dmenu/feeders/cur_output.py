#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for dmenu: Returns the current output name.

import i3


def get_prompt():
    return "Current output ->"


def get_current_output():
    workspaces = i3.msg('get_workspaces')
    workspace = i3.filter(tree=workspaces, focused=True)
    if workspace:
        return workspace[0]['output']
    else:
        return None


def feed():
    ''' Returns the current output (the output with focus) '''
    return get_current_output()


if __name__ == '__main__':
    print(feed())
