#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci_menu: Returns applications under paths.

import os
from subprocess import Popen, PIPE

import common

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
DMENU_PATH = os.path.normpath(os.path.join(MODULE_PATH,
                                           '../../../bin/dmenu_path'))


def get_prompt(free, output='all'):
    prompt = 'Start application'
    if free:
        prompt += " in a new workspace"
    if output == 'all':
        prompt += ' here'
    else:
        mon = common.get_natural_monitor_value(output)
        prompt += ' on {0}'.format(mon)
    return '{0} ->'.format(prompt)


def feed(win_inst=None, output='all'):
    ''' Returns a list of all found executables under paths.
    '''
    p = Popen(DMENU_PATH, stdout=PIPE, stderr=PIPE, shell=True)
    return p.stdout.read()


if __name__ == '__main__':
    print(feed())
