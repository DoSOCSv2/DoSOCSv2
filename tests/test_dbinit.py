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

from dosocs2 import dosocs2, configtools
from pytest import raises
from tempfile import NamedTemporaryFile

TEMP_CONFIG = '''
connection_uri = sqlite:///:memory:
namespace_prefix = sqlite:///:memory:
scanner_nomos_path = /dev/null
'''

def test_dbinit_typical_case_returns_zero(capsys):
    with NamedTemporaryFile(mode='w+') as tf:
        tf.write(TEMP_CONFIG)
        tf.flush()
        args = [
            'dbinit', 
            '--no-confirm',
            '-f',
            tf.name
            ]
        ret = dosocs2.main(args)
        assert ret == 0

def test_dbinit_warning_includes_connection_uri(capsys):
    with NamedTemporaryFile(mode='w+') as tf:
        tf.write(TEMP_CONFIG)
        tf.flush()
        args = [
            'dbinit', 
            '--no-confirm',
            '-f',
            tf.name
            ]
        ret = dosocs2.main(args)
        out, err = capsys.readouterr()
        assert 'sqlite:///:memory:' in err
