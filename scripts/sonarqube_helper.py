#!/usr/bin/env python2

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

import subprocess
import sys

package_path = sys.argv[1]

args = [
    'dosocs2', 'scan',
    '--scanners', 'nomos_deep',
    package_path
    ]
output = subprocess.check_output(args)
print output
