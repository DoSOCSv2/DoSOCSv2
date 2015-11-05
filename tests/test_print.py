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


from .helpers import TempEnv, run_dosocs2


TEMP_CONFIG = '''
connection_uri = sqlite:///{0}
namespace_prefix = sqlite:///{0}
scanner_copyright_path = /dev/null
scanner_dependency_check_path = /dev/null
scanner_monk_path = /dev/null
scanner_nomos_path = /dev/null
'''


def test_print_typical_case_returns_zero(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        args = [
            'scan', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        args = [
            'generate', 
            '-f',
            temp_config.name,
            '1'
            ]
        ret = run_dosocs2(args)
        args = [
            'print', 
            '-f',
            temp_config.name,
            '1'
            ]
        ret = run_dosocs2(args)
        assert ret == 0


def test_print_from_null_template_gives_empty_output(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        _ = capsys.readouterr()
        args = [
            'scan', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        args = [
            'generate', 
            '-f',
            temp_config.name,
            '1'
            ]
        ret = run_dosocs2(args)
        args = [
            'print', 
            '-f',
            temp_config.name,
            '-T',
            '/dev/null',
            '1'
            ]
        ret = run_dosocs2(args)
        out, _ = capsys.readouterr()
        assert 'SPDX' not in out
