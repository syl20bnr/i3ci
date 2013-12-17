#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci_menu: Returns the output names.

import i3


def get_prompt(send_workspace=False):
    if send_workspace:
        return "Send workspace to output ->"
    else:
        return "Send window to output ->"


def get_outputs_dictionary():
    ''' Returns a dictionary where key is a natural output name
    like "monitor 1" and value is the low level name like
    "xinerama-0"'''
    res = {}
    outputs = i3.msg('get_outputs')
    for i, o in enumerate(outputs):
        res['monitor {0}'.format(i+1)] = o['name']
    return res


def feed():
    outputs = get_outputs_dictionary()
    return sorted(outputs.keys())


if __name__ == '__main__':
    print('\n'.join(feed()))
