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

'''dosocs2 database initialization.'''

from __future__ import print_function

import json
import os
import pkg_resources
import sys

from sqlalchemy.sql import select


def msg(text, **kwargs):
    print('dosocs2' + ': ' + text, **kwargs)
    sys.stdout.flush()


def errmsg(text, **kwargs):
    print('dosocs2' + ': ' + text, file=sys.stderr, **kwargs)
    sys.stdout.flush()


def bulk_json_insert(conn, table, json_text):
    rows = json.loads(json_text)
    conn.execute(table.insert(), *rows)


def load_fixture(conn, schema, path):
    with open(path) as f:
        json_text = f.read()
    table_name, _ = os.path.splitext(os.path.basename(path))
    table = getattr(schema, table_name)
    bulk_json_insert(conn, table, json_text)


def discover_fixtures():
    fixtures_dir = pkg_resources.resource_filename('dosocs2', 'fixtures')
    return [
        os.path.join(fixtures_dir, path)
        for path in sorted(os.listdir(fixtures_dir))
        ]


def load_default_creator(conn, schema, creator_string):
    query = (
        select([schema.creator_types.c.creator_type_id])
        .where(schema.creator_types.c.name == 'Tool')
        )
    creator_type_id = conn.execute(query).fetchone()['creator_type_id']
    creator_params = {
        'creator_type_id': creator_type_id,
        'name': creator_string,
        'email': ''
        }
    conn.execute(schema.creators.insert().values(**creator_params))


def initialize(engine, schema, dosocs2_version):
    msg('dropping and creating all tables...', end='')
    schema.meta.drop_all(engine)
    schema.meta.create_all(engine)
    print('ok.')
    with engine.begin() as conn:
        msg('loading fixtures...')
        for fixture in discover_fixtures():
            msg('  {}...'.format(os.path.basename(fixture)), end='') 
            load_fixture(conn, schema, fixture)
            print('ok.')
        msg('loading default creator...', end='')
        load_default_creator(conn, schema, 'dosocs2-' + dosocs2_version)
        print('ok.')
        msg('committing changes...', end='')
    print('ok.')
    return True
