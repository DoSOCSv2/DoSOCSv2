# Copyright (C) 2015 University of Nebraska at Omaha
#
# This file is part of dosocs2.
#
# dosocs2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# dosocs2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dosocs2.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0+

import os
import re

DEFAULT_CONFIG = """\
# dosocs2 configuration file

# connection_uri = sqlite:////path/to/database.sqlite3
# or
# connection_uri = postgresql://user:pass@host:port/database
connection_uri = sqlite:////$(HOME)/.config/dosocs2/dosocs2.sqlite3

# comma-separated list of scanners to run when none is explicitly
# specified. For 'dosocs2 scan' and 'dosocs2 oneshot'
default_scanners = nomos

# new document namespace identifiers will start with this string
namespace_prefix = sqlite:///$(HOME)/.config/dosocs2/dosocs2.sqlite3

# If true, print all SQL statements to stdout as they are being executed
echo = False

############
# Scanners #
############

# Set the correct path for each
# If you used the included install-nomos.sh, the scanner_nomos_path
# should already be correct.
scanner_nomos_path = /usr/local/share/fossology/nomos/agent/nomossa

# optional ignore regex
# nomos will ignore files whose absolute path matches the regex
# scanner_nomos_ignore = .*\.class$
"""

XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))


class Config:

    def __init__(self):
        self.config_home = os.path.join(XDG_CONFIG_HOME, 'dosocs2')
        self.file_location = os.path.join(self.config_home, 'dosocs2.conf')
        self.config = self.get_from_file(DEFAULT_CONFIG.split('\n'))

    def _interpolate(self, matchobj):
        return os.environ.get(matchobj.group(1)) or ''

    def get_from_file(self, f):
        config = {}
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            key, val = line.strip().split('=', 1)
            key = key.strip()
            val = val.strip()
            val = re.sub(r'\$\((.*?)\)', self._interpolate, val)
            config[key] = val
        return config

    def make_config_dirs(self):
        try:
            os.makedirs(self.config_home)
        except EnvironmentError:
            pass

    def create_local_config(self, overwrite=True):
        self.make_config_dirs()
        if overwrite or not os.path.exists(self.file_location):
            with open(self.file_location, 'w') as f:
                f.write(DEFAULT_CONFIG)

    def update_config(self):
        try:
            with open(self.file_location) as f:
                self.config.update(self.get_from_file(f))
        except EnvironmentError:
            pass

    def dump_to_file(self, fileobj):
        for key, val in sorted(self.config.iteritems()):
            fileobj.write('{} = {}\n'.format(key, val))
