#!/usr/bin/env python2

from __future__ import print_function

import os
import subprocess
import sys

last_seen = None
packages = []

directory = sys.argv[1]

for subdir, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith(".jar") and '/.nexus/' not in subdir:
            packages.append((os.path.splitext(filename)[0], os.path.join(subdir, filename)))
            continue
for package_name, package_path in sorted(packages):
    print(package_name + '...', end='')
    sys.stdout.flush()
    args = [
        'dosocs2', 'scan',
        '--scanners', 'nomos_deep,dependency_check',
        '--package-name', '-'.join(package_name.split('-')[:-1]),
        '--package-comment', 'package_type=maven',
        '--package-version', package_name.split('-')[-1],
        package_path
        ]
    subprocess.call(args)
