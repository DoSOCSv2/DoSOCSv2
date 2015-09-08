#!/usr/bin/env python2

# Copyright (C) 2015 University of Nebraska at Omaha
# Copyright (C) 2015 Thomas T. Gurney
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

from __future__ import print_function

import os
import subprocess
import sys

packages = []

directory = sys.argv[1]

for subdir, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith(".jar") and '/.nexus/' not in subdir:
            packages.append((os.path.splitext(filename)[0], os.path.join(subdir, filename)))

for package_name, package_path in sorted(packages):
    print(package_name + '...')
    args = [
        'dosocs2', 'scan',
        '--scanners', 'nomos_deep,dependency_check',
        '--package-name', '-'.join(package_name.split('-')[:-1]),
        '--package-comment', 'package_type=maven',
        '--package-version', package_name.split('-')[-1],
        package_path
        ]
    subprocess.call(args)
