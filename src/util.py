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

import jinja2
import magic
import hashlib


def render_template(templatefile, context):
    with open(templatefile, 'r') as f:
        s = f.read()
    t = jinja2.Template(s)
    return t.render(context)


def spdx_filetype(filename):
    magic_string = magic.from_file(filename)
    if (' source' in magic_string and ' text' in magic_string or
        ' script' in magic_string and ' text' in magic_string or
        ' program' in magic_string and ' text' in magic_string or
        ' shell script' in magic_string or
        ' text executable' in magic_string or
        'HTML' in magic_string and 'text' in magic_string or
        'XML' in magic_string and 'text' in magic_string):
        return 'SOURCE'
    if (' executable' in magic_string or
        ' relocatable' in magic_string or
        ' shared object' in magic_string or
        ' dynamically linked' in magic_string or
        ' ar archive' in magic_string):
        return 'BINARY'
    if ('archive' in magic_string):
        return 'ARCHIVE'
    return 'OTHER'


def sha1(filename):
    with open(filename, 'rb') as f:
        lines = f.read()
    checksum = hashlib.sha1(lines).hexdigest()
    return checksum
