# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2015 University of Nebraska Omaha and other contributors.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import shutil

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
scanner_nomos_path = /usr/share/fossology/nomos/agent/nomos
scanner_copyright_path = /usr/share/fossology/copyright/agent/copyright
scanner_monk_path = /usr/share/fossology/monk/agent/monk
scanner_dependency_check_path = /path/to/dependency-check.sh
"""

XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
DOSOCS2_CONFIG_HOME = os.path.join(XDG_CONFIG_HOME, 'dosocs2')
DOSOCS2_CONFIG_PATH = os.path.join(DOSOCS2_CONFIG_HOME, 'dosocs2.conf')
GLOBAL_CONFIG_PATH = '/etc/dosocs2.conf'

config = {}

def _interpolate(matchobj):
    return os.environ.get(matchobj.group(1)) or ''


def get_config_from_file(f):
    config = {}
    for line in f:
        if not line.strip() or line.startswith('#'):
            continue
        key, val = line.strip().split('=', 1)
        key = key.strip()
        val = val.strip()
        val = re.sub(r'\$\((.*?)\)', _interpolate, val)
        config[key] = val
    return config


def get_config_resolution_order(other_config_path=None):
    return [
        GLOBAL_CONFIG_PATH,
        other_config_path or DOSOCS2_CONFIG_PATH
        ]


def create_user_config(overwrite=True):
    try:
        os.makedirs(DOSOCS2_CONFIG_HOME)
    except EnvironmentError:
        pass
    try:
        if overwrite or not os.path.exists(DOSOCS2_CONFIG_PATH):
            with open(DOSOCS2_CONFIG_PATH, 'w') as f:
                f.write(DEFAULT_CONFIG)
    except EnvironmentError:
        return False
    return True


def update_config(other_config_path=None):
    global config
    config_order = get_config_resolution_order(other_config_path)
    config.update(get_config_from_file(DEFAULT_CONFIG.split('\n')))
    for path in config_order:
        try:
            with open(path) as f:
                config.update(get_config_from_file(f))
        except EnvironmentError:
            continue


def dump_to_file(fileobj):
    for key, val in sorted(config.iteritems()):
        fileobj.write('{} = {}\n'.format(key, val))

update_config()
