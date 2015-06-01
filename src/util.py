# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2015 University of Nebraska Omaha and other contributors.

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

from contextlib import contextmanager
import hashlib
import jinja2
import magic
import os
import shutil
import tarfile
import tempfile
import uuid
import zipfile


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


@contextmanager
def tempextract(path):
    try:
        tempdir = tempfile.mkdtemp()
        if tarfile.is_tarfile(path):
            with tarfile.open(path) as tf:
                relpaths = tf.getnames()
                tf.extractall(path=tempdir)
            yield (tempdir, relpaths)
        elif zipfile.is_zipfile(path):
            with zipfile.open(path) as zf:
                relpaths = zf.namelist()
                zf.extractall(path=tempdir)
            yield (tempdir, relpaths)
    finally:
        shutil.rmtree(tempdir)


def gen_ver_code(hashes, excluded_hashes=None):
    if excluded_hashes is None:
        excluded_hashes = set()
    hashes_less_excluded = (h for h in hashes if h not in excluded_hashes)
    hashblob = ''.join(sorted(hashes_less_excluded))
    return hashlib.sha1(hashblob).hexdigest()


def package_friendly_name(package_file_name):
    newname = os.path.splitext(package_file_name)[0]
    if newname.endswith('.tar'):
        newname = os.path.splitext(newname)[0]
    return newname


def gen_id_string():
    return 'SPDXRef-' + str(uuid.uuid4())
