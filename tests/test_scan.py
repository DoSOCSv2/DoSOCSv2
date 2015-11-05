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


def test_scan_typical_case_returns_zero(capsys):
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
        assert ret == 0


def test_scan_prints_package_id_to_stderr(capsys):
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
        out, err = capsys.readouterr()
        assert '/dev/null: package_id: 1' in err


def test_scan_already_ran_on_package_wont_run_again(capsys):
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
        _ = capsys.readouterr()
        ret_again = run_dosocs2(args)
        out, err = capsys.readouterr()
        assert 'dummy already ran on package 1' in err


def test_scan_explicit_rescan_acknowledged(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        args = [
            'scan', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '-r',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        _ = capsys.readouterr()
        ret_again = run_dosocs2(args)
        out, err = capsys.readouterr()
        assert 'dummy already ran' not in err
