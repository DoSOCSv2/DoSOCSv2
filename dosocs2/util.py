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

'''Miscellaneous utility functions.'''

from __future__ import print_function

from contextlib import contextmanager
import hashlib
import os
import re
import shutil
import sys
import tarfile
import tempfile
import uuid
import zipfile

import magic

def is_source(magic_string):
    return (
        ' source' in magic_string and ' text' in magic_string or
        ' script' in magic_string and ' text' in magic_string or
        ' program' in magic_string and ' text' in magic_string or
        ' shell script' in magic_string or
        ' text executable' in magic_string or
        'HTML' in magic_string and 'text' in magic_string or
        'XML' in magic_string and 'text' in magic_string
        )

def is_binary(magic_string):
    return (
        ' executable' in magic_string or
        ' relocatable' in magic_string or
        ' shared object' in magic_string or
        ' dynamically linked' in magic_string or
        ' ar archive' in magic_string
        )

def spdx_filetype(filename):
    '''Try to guess the SPDX filetype of the file.'''
    magic_string = magic.from_file(filename)
    if is_source(magic_string):
        return 'SOURCE'
    if is_binary(magic_string):
        return 'BINARY'
    if 'archive' in magic_string:
        return 'ARCHIVE'
    return 'OTHER'


def sha1(filename):
    with open(filename, 'rb') as f:
        lines = f.read()
    checksum = hashlib.sha1(lines).hexdigest()
    return checksum


def archive_type(path):
    if tarfile.is_tarfile(path):
        return 'tar'
    elif zipfile.is_zipfile(path):
        return 'zip'
    else:
        return None

@contextmanager
def tempextract(path):
    try:
        tempdir = tempfile.mkdtemp()
        ar_type = archive_type(path)
        if ar_type == 'tar':
            with tarfile.open(path) as tf:
                relpaths = tf.getnames()
                tf.extractall(path=tempdir)
            yield (tempdir, relpaths)
        elif ar_type == 'zip':
            with zipfile.ZipFile(path) as zf:
                relpaths = zf.namelist()
                zf.extractall(path=tempdir)
            yield (tempdir, relpaths)
        else:
            raise TypeError('{} is not an archive file'.format(path))
    finally:
        shutil.rmtree(tempdir)


def gen_ver_code(hashes, excluded_hashes=None):
    '''Generate and return SPDX package verification code.'''
    if excluded_hashes is None:
        excluded_hashes = set()
    hashes_less_excluded = (h for h in hashes if h not in excluded_hashes)
    hashblob = ''.join(sorted(hashes_less_excluded))
    return hashlib.sha1(hashblob).hexdigest()


def package_friendly_name(package_file_name):
    '''Return name of a package, without extension.'''
    newname = os.path.splitext(package_file_name)[0]
    if newname.endswith('.tar'):
        newname = os.path.splitext(newname)[0]
    return newname


def file_name_for_id(file_name):
    new1 = os.path.basename(file_name)
    # strip illegal chars, limit to 20 chars
    return re.sub(r'[^A-Za-z0-9]', '_', new1)[:20]


def gen_id_string(prefix='element', file_name=None, sha1=None):
    '''Generate and return an SPDX identifier.'''
    uuid4 = str(uuid.uuid4())
    if sha1 is None:
        sha1part = uuid4[24:28]
    else:
        sha1part = sha1[:4]
    suffix = sha1part + '-' + uuid4[:8]
    new_file_name = file_name_for_id(file_name or uuid4[19:23])
    pieces = 'SPDXRef', prefix, new_file_name, suffix
    return '-'.join(pieces)


def row_to_dict(row):
    '''Convert SQLSoup row to a dictionary.'''
    d = {}
    for column in row._table.columns:
        d[column.name] = getattr(row, column.name)
    return d


def rows_to_dicts(rows):
    return [row_to_dict(row) for row in rows]


def lookup_by_sha1(table, sha1):
    '''Lookup object by SHA-1 sum and return the object, or None.

    'table' argument must be a table object as created by SQLSoup.
    '''
    # Maybe shouldn't be using first() here?
    # Freak occurence of sha1 collision probably won't happen.
    # But if it does, this will give nondeterministic results.
    # (although, you will have bigger problems...)
    return table.filter(table.sha1 == sha1).first()


def friendly_namespace_suffix(doc_name):
    '''Return a namespace suffix based on an SPDX document name.'''
    return '/' + doc_name + '-' + str(uuid.uuid4())


def allpaths(path):
    for (root, dirnames, filenames) in os.walk(path):
        for dirname in dirnames:
            yield os.path.join(root, dirname)
        for filename in filenames:
            yield os.path.join(root, filename)


def get_dir_hashes(path, excluded_hashes=None):
    '''Return a (str, dict) pair: (ver_code, {filepath: sha1})

    ver_code: Package verification code for the directory `path`
    filepath: Relative path to a file
    sha1: SHA-1 hex string for that file
    '''
    hashes = {relpath: sha1(relpath)
              for relpath in allpaths(path)
              if os.path.isfile(relpath)
              }
    return (gen_ver_code(hashes.values(), excluded_hashes), hashes)
