# 2013 syl20bnr <sylvain.benner@gmail.com>
#
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License (WTFPL), Version
# 2, as published by Sam Hocevar. See http://sam.zoy.org/wtfpl/COPYING for more
# details.
import re
from subprocess import Popen, PIPE


LED_STATUSES_CMD = 'xset q | grep "LED mask"'
LED_MASKS = [
    ('caps',   0b0000000001,   'CAPS',   '#DC322F'),
    ('num',    0b0000000010,    'NUM',   '#859900'),
    ('scroll', 0b0000000100, 'SCROLL',   '#2AA198'),
    ('altgr',  0b1111101000,  'ALTGR',   '#B58900')]


class Py3status:

    def __init__(self):
        self._mask = None

    def a(self, json, i3status_config):
        ''' Return one LEDs status. '''
        self._mask = None
        response = self._get_led_statuses(0)
        return (0, response)

    # def b(self, json, i3status_config):
    #     ''' Return one LEDs status. '''
    #     response = self._get_led_statuses(1)
    #     return (0, response)

    # def c(self, json, i3status_config):
    #     ''' Return one LEDs status. '''
    #     response = self._get_led_statuses(2)
    #     return (0, response)

    # def d(self, json, i3status_config):
    #     ''' Return one LEDs status. '''
    #     response = self._get_led_statuses(3)
    #     return (0, response)

    def stop(self):
        ''' Exit nicely '''
        self.kill = True

    def _get_led_statuses(self, index):
        ''' Return a list of dictionaries representing the current keyboard LED
        statuses '''
        (n, m, t, c) = LED_MASKS[index]
        # if not self._mask:
        #     try:
        #         p = Popen(LED_STATUSES_CMD, stdout=PIPE, shell=True)
        #         self._mask = re.search(r'[0-9]{8}', p.stdout.read())
        #     except Exception:
        #         return Py3status._to_dict(n, 'YYYYESS', c)
        # if self._mask:
        #     v = int(self._mask.group(0))
        #     if v & m:
        #         return Py3status._to_dict(n, t, c)
        return Py3status._to_dict(n, 'NOOOO', c)

    @staticmethod
    def _to_dict(name, text, color):
        ''' Return a dictionary with given information '''
        return {'full_text': text, 'name': name, 'color': color}
