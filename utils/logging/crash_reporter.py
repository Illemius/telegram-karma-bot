"""
from Illemius/BotCorePlatform/pyBot
"""

import os
import time
import traceback
import uuid

from meta import CRASHREPORT_LOCATION
from .dmesg import dmesg


def check_report_path():
    # Check crash reports directory
    if not os.path.exists(CRASHREPORT_LOCATION):
        os.mkdir(CRASHREPORT_LOCATION)


class CrashReport:
    def __init__(self, exc_type, exc_value, exc_traceback):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback
        self.time = time.localtime()
        self.id = str(uuid.uuid4())
        self.formatted_traceback = traceback.format_exception(self.exc_type, self.exc_value, self.exc_traceback)

        self.lines = []

        self.filename = 'report_{datetime}.log'.format(
            datetime=time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
        self.file = os.path.join(CRASHREPORT_LOCATION, self.filename)

    def add_message(self, message):
        self.lines.append(message)

    def add_splitter(self, symbol='=', length=80):
        self.add_message(symbol * length)

    def save(self):
        check_report_path()

        # Write report
        with open(self.file, 'w') as file:
            file.write('Title: ' + self.get_header() + '\n')
            file.write('Date: ' + time.strftime("%d.%m.%Y", self.time) + '\n')
            file.write('Time: ' + time.strftime("%H:%M:%S", self.time) + '\n\n')
            file.write('ID: ' + self.id + '\n\n')
            if len(self.lines) > 0:
                file.write('\n'.join(self.lines) + '\n\n')
            file.write('\n'.join(self.formatted_traceback))

        dmesg('Crash report "{}" saved to: "{}"'.format(self.get_header(), self.file), group='fs')

    def get_header(self):
        return traceback.format_exception(self.exc_type, self.exc_value, self.exc_traceback)[-1].rstrip('\n')

    def __str__(self):
        return self.get_header()

    def __repr__(self):
        return '<CrashReport "{}">'.format(self.__str__())
