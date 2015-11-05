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


def test_configtest_expected_output_typical_case(capsys):
    with NamedTemporaryFile(mode='w+') as tf:
        tf.write('''
connection_uri = sqlite:///:memory:
namespace_prefix = sqlite:///:memory:
scanner_nomos_path = /dev/null
''')
        tf.flush()
        expected = '''
-------------------------------------------------------------------------------

Config location:
{}

-------------------------------------------------------------------------------

Effective configuration:

# begin dosocs2 config

connection_uri = sqlite:///:memory:
default_scanners = nomos
echo = False
namespace_prefix = sqlite:///:memory:
scanner_nomos_path = /dev/null

# end dosocs2 config

-------------------------------------------------------------------------------

Testing specified scanner paths...
nomos (/dev/null)...ok.

-------------------------------------------------------------------------------

Testing database connection...ok.
'''.format(tf.name)
        args = [
            'configtest', 
            '-f',
            tf.name
            ]
        dosocs2.main(args)
    out, err = capsys.readouterr()
    assert out == expected
