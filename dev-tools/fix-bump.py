#!/usr/bin/python2

import sys

version_string = sys.argv[1]

major, minor, fix = [int(x) for x in version_string.split('.')]

print '{}.{}.{}'.format(major, minor, fix+1)
