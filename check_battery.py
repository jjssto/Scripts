#!/usr/bin/env python3
#
# check_battery.py
#
# Creted by: jjssto <jjssto@posteo.de>, 2020-04-16T21:41:37.383Z

import re
import time

PATH = "/sys/class/power_supply/BAT0/uevent"
THRESHOLD = 0.05

def energy_level():
    ''' class to get charge of battery'''
    with open(PATH, 'r') as f:
        for line in f:
            if ((m := re.match(r'POWER_SUPPLY_ENERGY_NOW=(.*)', line)) is
                    not None):
                energy_now = float(m.group(1))
            elif ((m := re.match(r'POWER_SUPPLY_ENERGY_FULL=(.*)', line))
                    is not None):
                energy_full = float(m.group(1))
    return(energy_now / energy_full)

def energy_source():
    """
    Returns True if source is battery

    Returns:
    --------
    bool
        indicates if the source is the battery.
    """
    with open(PATH, 'r') as f:
        for line in f:
            if ( m := re.match(r'.*STATUS=(.*)', line)) is not None:
                if re.search(r".*Discharging.*", m.group(1)) is not None:
                    return(True)
                else:
                    return(False)
        else:
            return(False)


if __name__ == "__main__":
    while True:
        charge = energy_level()
        if charge < THRESHOLD:
            sp.call(['/home/josef/.local/bin/i3exit','suspend'])
        else:
            time.sleep(60)
