# Copyright (C) 2015 University of Nebraska at Omaha
# Copyright (C) 2015 dosocs2 contributors
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

from dosocs2 import dosocs2, configtools
from pytest import raises
from tempfile import NamedTemporaryFile

TEMP_CONFIG = '''
connection_uri = sqlite:///{0}
namespace_prefix = sqlite:///{0}
scanner_copyright_path = /dev/null
scanner_dependency_check_path = /dev/null
scanner_monk_path = /dev/null
scanner_nomos_path = /dev/null
'''

def test_oneshot(capsys):
    with NamedTemporaryFile(mode='w+') as tf:
        with NamedTemporaryFile(mode='w+') as tmpdb:
            # TODO: Move this setup logic to a new context manager
            tf.write(TEMP_CONFIG.format(tmpdb.name))
            tf.flush()
            args = [
                'dbinit', 
                '-f',
                tf.name,
                '--no-confirm'
                ]
            ret = dosocs2.main(args, config=configtools.Config(global_path='/dev/null'))
            args = [
                # TODO: Add document comment and other optional args
                # then assert that they show up in the resulting doc
                'oneshot', 
                '-f',
                tf.name,
                '/dev/null'
                ]
            ret = dosocs2.main(args, config=configtools.Config(global_path='/dev/null'))
            assert ret == 0
