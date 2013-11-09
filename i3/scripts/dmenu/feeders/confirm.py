#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for dmenu: Returns Ok, Cancel tokens :-)


def get_prompt(action):
    return "Confirm {0} ? ->".format(action)


def feed():
    ''' Return a list of logout command. '''
    return ['OK', 'Cancel']


if __name__ == '__main__':
    print('\n'.join(feed()))
