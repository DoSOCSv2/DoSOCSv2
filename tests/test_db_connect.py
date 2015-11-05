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

from dosocs2 import schema as db
from pytest import raises

def test_db_create_connection_with_echo():
    engine = db.create_connection('sqlite:///:memory:', echo=True)
    assert engine is not None
    assert engine._echo

def test_db_create_connection_without_echo():
    engine = db.create_connection('sqlite:///:memory:', echo=False)
    assert engine is not None
    assert not engine._echo

def test_db_create_connection_only_one_arg_fails():
    with raises(Exception):
        engine = db.create_connection('sqlite:///:memory:')

def test_db_create_connection_bad_conn_string_fails():
    with raises(Exception):
        engine = db.create_connection('blah', echo=True)
