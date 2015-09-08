#!/bin/bash

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

[[ "$1" == "" ]] && printf 'You must specify a file argument\n' && exit 1

LIBSFILE=$1

# the below regex converts the 'pip list' style to the 'pip freeze'
# style of package spec
cat $LIBSFILE | sed -r 's/ \((.*?)\)/==\1/g' | while read item; do
    pip install -d . --no-binary :all: --no-compile -I $item
done
     
shopt -s nullglob
for item in *.bz2 *.gz *.zip *.tar; do
   PVERSION=$(ls -1 $item | grep -Eo '[0-9]+\.[0-9]+(\.[0-9]+)?')
   PNAME=$(ls -1 $item | sed -r 's/-[0-9]+\.[0-9]+(\.[0-9]+)?.*//g')
   dosocs2 scan --package-version=$PVERSION --package-name=$PNAME --package-comment="package_type=python" $item
done
shopt -u nullglob
