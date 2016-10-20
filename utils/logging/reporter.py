"""
from Illemius/BotCorePlatform/pyBot
Analog of CrashReporter
"""

import os
import time

from .dmesg import dmesg
from meta import REPORTS_LOCATION


def report_path():
    # Check crash reports directory
    if not os.path.exists(REPORTS_LOCATION):
        os.mkdir(REPORTS_LOCATION)


class Report:
    def __init__(self, name=''):
        self.name = name
        self.time = time.localtime()

        self._lines = []

        self.filename = '{name}_{datetime}.txt'.format(
            name=self.name,
            datetime=time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
        self.file = os.path.join(REPORTS_LOCATION, self.filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def new_line(self, message=''):
        self._lines.append(message)

    def add_splitter(self, symbol='=', length=80):
        self.new_line(symbol * length)

    def save(self):
        report_path()

        # Write report
        with open(self.file, 'w') as file:
            file.write('Title: ' + self.name + '\n')
            file.write('Date: ' + time.strftime("%d.%m.%Y", self.time) + '\n')
            file.write('Time: ' + time.strftime("%H:%M:%S", self.time) + '\n\n')
            if len(self._lines) > 0:
                file.write('\n'.join(self._lines) + '\n\n')

        dmesg('Write file "{}"'.format(self.file), group='fs')

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Report "{}">'.format(self.__str__())
