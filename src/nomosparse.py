# <SPDX-License-Identifier: Apache-2.0>

# Copyright (c) 2015 doSOCS contributors.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Parse the output of the nomos license scanner.'''
import re

pattern = re.compile('File (.+?) contains license\(s\) (.+)')


def parser(iterable):
    m = None
    for item in iterable:
        m = re.match(pattern, item)
        if m is None:
            continue
        yield [m.group(1), m.group(2)]


def parse_one(s):
    p = parser([s])
    for single_item in p:
        return single_item
