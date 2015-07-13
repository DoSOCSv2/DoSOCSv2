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

from ConfigParser import RawConfigParser
import pkg_resources
import os
import shutil

DEFAULT_CONFIG_PATH = pkg_resources.resource_filename('dosocs2', 'default/dosocs2.conf')
XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
DOSOCS2_CONFIG_HOME = os.path.join(XDG_CONFIG_HOME, 'dosocs2')
DOSOCS2_CONFIG_PATH = os.path.join(DOSOCS2_CONFIG_HOME, 'dosocs2.conf')

config = None
connection_uri = None
namespace_prefix = None
_parser = None

def create_user_config(overwrite=True):
    try:
        os.makedirs(DOSOCS2_CONFIG_HOME)
    except EnvironmentError:
        pass
    try:
        if overwrite or not os.path.exists(DOSOCS2_CONFIG_PATH):
            shutil.copyfile(DEFAULT_CONFIG_PATH, DOSOCS2_CONFIG_PATH)
    except EnvironmentError:
        return False
    return True


def update_config(other_config_path=None):
    global config
    global connection_uri
    global namespace_prefix
    global _parser
    _parser = RawConfigParser()
    _parser.read([DEFAULT_CONFIG_PATH, other_config_path or DOSOCS2_CONFIG_PATH])
    config = {section: dict(_parser.items(section))
              for section in _parser.sections()
              }
    uri_fmt = '{dbms}://{user}:{password}@{host}:{port}/{database}'
    connection_uri = uri_fmt.format(**config['database'])
    prefix_fmt = '{dbms}://{host}:{port}/{database}'
    namespace_prefix = prefix_fmt.format(**config['database'])

def config_location(other_config_path=None):
    if os.path.exists(other_config_path or DOSOCS2_CONFIG_PATH):
        return other_config_path or DOSOCS2_CONFIG_PATH
    return DEFAULT_CONFIG_PATH

def dump_to_file(fileobj):
    global _parser
    _parser.write(fileobj)

update_config()
