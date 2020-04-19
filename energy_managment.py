#!/usr/bin/env python3
#
# energy_managment.py
#
# Creted by: jjssto <jjssto@posteo.de>, 2020-04-17T06:02:38.585Z
"""
The script module energy_managment.py suspends the computer, if the
battery is nearly empty or if the user is idle for a certain time
"""
import os
import subprocess as sp
import time
import re
home = os.environ.get('HOME')
dir = home + '/.local/bin/'
os.chdir(dir)
import check_battery
CONFIG = home + '/.config/energy_managment.conf'


def idle_time():
    """
    Returns the idle time of the userguide

    Args:
        None

    Returns:
        float: seconds since the last user action
    """


    ret = sp.run(['xssstate','-i'], capture_output = True)
    user_idle = float(ret.stdout)
    return(user_idle / 1000)


def suspend():
    """
    Suspends the computer
    """
    sp.run(['i3exit','suspend-then-hibernate'])


def brightness(level):
    """
    Sets the brightness of the screen

    Args:
    -----
    energy_level : int
        brighness of the screen (between 0 and 100)
    """
    sp.run(['light','-S',str(level)])

class Manager:
    """
    Power managment

    Attributes:
    -----------

    suspend_idle : bool

    suspend_idle_plugged : bool

    idle_threshold : float

    idle_plugged_threshold : float

    idle_dim : bool

    idle_dim_threshold : float

    battery_threshold : float


    Methods:
    --------
    manage(interval)
        power managment
    """
    def __init__(self):
        self.__update()

    def __update(self):
        self.suspend_idle = bool(self.__get_definition('SUSPEND_IDLE'))
        self.suspend_idle_plugged = bool(
            self.__get_definition('SUSPEND_IDLE_PLUGGED')
            )
        self.idle_threshold = float(self.__get_definition('SUSPEND_IDLE_THR'))
        self.idle_plugged_threshold = float(
            self.__get_definition('SUSPEND_IDLE_THR_PLUGGED')
            )

        self.idle_dim = bool(self.__get_definition('IDLE_DIM'))
        self.idle_dim_threshold = float(self.__get_definition('IDLE_DIM_THR'))

        self.battery_threshold = float(self.__get_definition('BATTERY_THR'))

    def __get_definition(self, string):
        with open(CONFIG, 'r') as f:
            for line in f:
                if (m := re.match((string + r' (.*)'), line)) is not None:
                    return(m.group(1))
            else:
                return("")


    def manage(self, interval):
        """
        Suspends the computer if the user is idle or if the battery is nearly
        empty

        Args:
        -----
        interval : int
            interval between checks (in seconds)
        """
        while True:
            self.__update()
            level = check_battery.energy_level()
            print(level)
            idle = idle_time()
            print(idle)
            if check_battery.energy_source():
                # energy source is battery
                if level < self.battery_threshold:
                    suspend()
                elif self.suspend_idle:
                    if idle > self.idle_threshold:
                        suspend()
                if self.idle_dim and idle > self.idle_dim_threshold:
                    brightness(1)
            else:
                # energy source is not the battery
                if self.suspend_idle_plugged:
                    if idle > self.idle_plugged_threshold:
                        suspend()
            time.sleep(interval)


if __name__ == "__main__":
    manager = Manager()
    manager.manage(60)
