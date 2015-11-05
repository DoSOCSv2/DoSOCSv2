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

from contextlib import contextmanager
from dosocs2 import dosocs2, configtools
from tempfile import NamedTemporaryFile

@contextmanager
def TempEnv(config_text):
    with NamedTemporaryFile(mode='w+') as temp_config:
        with NamedTemporaryFile(mode='w+') as temp_db:
            temp_config.write(config_text.format(temp_db.name))
            temp_config.flush()
            args = [
                'dbinit', 
                '-f',
                temp_config.name,
                '--no-confirm'
                ]
            ret = run_dosocs2(args)
            yield temp_config, temp_db


def run_dosocs2(args):
    return dosocs2.main(args)
