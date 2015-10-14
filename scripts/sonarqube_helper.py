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

# Helper script for dosocs2 SonarQube plugin.

import os
import re
import subprocess
import sys
import psycopg2

package_path = sys.argv[1]

args = [
    'dosocs2', 'scan',
    '--scanners', 'nomos_deep,dependency_check',
    package_path
    ]
output = subprocess.check_output(args, stderr=subprocess.STDOUT)
print output
m = re.search(r"package_id: ([0-9]+)\n", output)
package_id = m.group(1)

query = """
select pac.package_id, short_name, count(fli.file_license_id) found_count, package_comment
from packages pac
join packages_files pfi on  pac.package_id = pfi.package_id
join files fil on pfi.file_id = fil.file_id
join files_licenses fli on fil.file_id = fli.file_id
join licenses lic on fli.license_id = lic.license_id
where pac.package_id = ?
group by short_name
"""
conn = psycopg2.connect('dbname=spdx user=spdx') # add password parameter
c = conn.cursor()
c.execute(query, (package_id,))
print c.fetchall()
