#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci-menu: Returns a list of logout commands

import getpass


def get_prompt():
    return "logout {0} ->".format(getpass.getuser())


def feed():
    ''' Return a list of logout command. '''
    return ['logout',
            'suspend',
            'reboot',
            'shutdown']


if __name__ == '__main__':
    print('\n'.join(feed()))
