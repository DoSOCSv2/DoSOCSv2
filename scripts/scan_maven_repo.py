#!/usr/bin/env python2

from __future__ import print_function

import os
import psycopg2
import subprocess
import sys

last_seen = None
packages = []

directory = sys.argv[1]

for subdir, dirnames, filenames in os.walk(directory):
    if last_seen is not None and subdir.startswith(last_seen):
        continue
    for filename in filenames:
        if filename.endswith(".pom") and '/.nexus/' not in subdir:
            last_seen = subdir
            packages.append((os.path.splitext(filename)[0], subdir))
            continue

for package_name, package_dir in sorted(packages):
    print(package_name + '...', end='')
    sys.stdout.flush()
    args = [
        'dosocs2', 'scan',
        '--scanner', 'nomos_deep',
        '--package-name', '-'.join(package_name.split('-')[:-1]),
        '--package-comment', 'package_type=maven',
        '--package-version', package_name.split('-')[-1],
        package_dir
        ]
    subprocess.call(args)
