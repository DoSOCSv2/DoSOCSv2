# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2014-2015 University of Nebraska at Omaha (UNO) and other
# contributors.

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


import copy
import itertools
import os
import string

from sqlalchemy.sql import select

from . import config
from . import schema as db
from . import util


def insert(conn, table, params):
    query = table.insert.values(**params)
    result = conn.execute(query)
    [pkey] = result.inserted_primary_key
    return pkey


def lookup_license(conn, short_name):
    query = (
        select([db.licenses])
        .where(db.licenses.c.short_name == short_name)
        )
    return dict(**conn.execute(query).fetchone())


def lookup_or_add_license(conn, short_name, comment=None):
    '''Add license to the database if it does not exist.

    Return the new or existing license object in any case.
    '''
    transtable = string.maketrans('()[]<>', '------')
    short_name = string.translate(short_name, transtable)
    existing_license = lookup_license(short_name)
    if existing_license is not None:
        return existing_license
    new_license = {
        # correct long name is never known for found licenses
        'name': None,
        'short_name': short_name,
        'cross_reference': '',
        'comment': comment or '',
        'is_spdx_official': False,
        }
    new_license['license_id'] = insert(conn, db.licenses, new_license)
    return new_license


def create_file(conn, path, known_sha1):
    file_type_query = (
        select([db.file_types.c.file_type_id])
        .where(db.file_types.c.name == util.spdx_filetype(path))
        )
    [file_type_id] = conn.execute(file_type_query).fetchone()
    new_file = {
        'sha1': known_sha1,
        'file_type_id': file_type_id,
        'copyright_text': None,
        'project_id': None,
        'comment': '',
        'notice': ''
        }
    new_file['file_id'] = insert(conn, db.files, new_file)
    return new_file


def store_scan_result(conn, scanner_name, scan_result, path_file_id_map):
    for path in scan_result:
        licenses_found = [
            lookup_or_add_license(shortname, 'found by ' + scanner_name)
            for shortname in scan_result[path]
            ]
        for license in licenses_found:
            file_license_params = {
                'file_id': path_file_id_map[path],
                'license_id': license['license_id'],
                'extracted_text': '',
                }
            insert(conn, db.files_licenses, file_license_params)


def scan_file(conn, path, scanner, known_sha1=None):
    '''Scan file for licenses, and add it to the DB if it does not exist.

    Return the file object.

    If the file is cached, return the cached file object, and do not
    scan.
    '''
    sha1 = known_sha1 or util.sha1(path)
    file = util.lookup_by_sha1(db.files, sha1)
    if file is not None:
        return file
    file = create_file(path, sha1)
    scan_result = scanner.scan_file(path)
    self.store_scan_result(scanner.name, scan_result, {path: file['file_id']})
    return file


def scan_directory(conn, path, scanner, name=None, version=None, comment=None, file_name=None, sha1=None):
    ver_code, hashes = util.get_dir_hashes(path)
    package = {
        'name': name or os.path.basename(os.path.abspath(path)),
        'version': version or '',
        'file_name': file_name or os.path.basename(os.path.abspath(path)),
        'supplier_id': None,
        'originator_id': None,
        'download_location': None,
        'verification_code': ver_code,
        'ver_code_excluded_file_id': None,
        'sha1': sha1,  # None is permitted here
        'home_page': None,
        'source_info': '',
        'concluded_license_id': None,
        'declared_license_id': None,
        'license_comment': '',
        'copyright_text': None,
        'summary': '',
        'description': '',
        'comment': ''
        }
    package['package_id'] = insert(conn, db.packages, package)
    for (filepath, sha1) in hashes.iteritems():
        fileobj = scan_file(filepath, scanner, known_sha1=sha1)
        package_file_params = {
            'package_id': package['package_id'],
            'file_id': fileobj['file_id'],
            'concluded_license_id': None,
            'file_name': os.path.join(os.curdir, os.path.relpath(filepath, start=path)),
            'license_comment': ''
            }
        insert(conn, db.packages_files, package_file_params)
    self.db.flush()
    return package

def scan_package(self, path, scanner, name=None, version=None, comment=None):
    '''Scan package for licenses. Add it and all files to the DB.

    Return the package object.

    Only scan if the package is not already cached (by SHA-1).
    '''
    if os.path.isdir(path):
        return self.scan_directory(path, scanner=scanner, name=name, version=version)
    sha1 = util.sha1(path)
    package = util.lookup_by_sha1(db.packages, sha1)
    if package is not None:
        return package
    with util.tempextract(path) as (tempdir, relpaths):
        kwargs = {
            'path': tempdir,
            'scanner': scanner,
            'name': name or util.package_friendly_name(os.path.basename(path)),
            'version': version,
            'comment': comment,
            'file_name': os.path.basename(os.path.abspath(path)),
            'sha1': sha1
            }
        package = scan_directory(**kwargs)
    return package

def create_document_namespace(self, doc_name):
    suffix = util.friendly_namespace_suffix(doc_name)
    uri = config.namespace_prefix + suffix
    doc_namespace = {'uri': uri}
    doc_namespace['document_namespace_id'] = insert(conn, db.document_namespaces, doc_namespace)
    return doc_namespace

# must rewrite
def create_all_identifiers(self, document_namespace_id, package_id):
    all_files = (
        self.db.packages_files
        .filter(self.db.packages_files.package_id == package_id)
        .all()
        )
    identifier_ids = []
    package = self.db.packages.get(package_id)
    package_id_params = {
        'document_namespace_id': document_namespace_id,
        'package_id': package_id,
        'id_string': util.gen_id_string('package', package.file_name, package.sha1)
        }
    for file in all_files:
        filesha1 = self.db.files.get(file.file_id).sha1
        file_id_params = {
            'document_namespace_id': document_namespace_id,
            'package_file_id': file.package_file_id,
            'id_string': util.gen_id_string('file', file.file_name, filesha1)
            }
        file_identifier = self.db.identifiers.insert(**file_id_params)
        self.db.flush()
        identifier_ids.append(file_identifier.identifier_id)
    package_identifier = self.db.identifiers.insert(**package_id_params)
    self.db.flush()
    identifier_ids.append(package_identifier.identifier_id)
    return identifier_ids

# must rewrite
def create_relationship(self, left_id, rel_type, right_id):
    relationship_params = {
        'left_identifier_id': left_id,
        'relationship_type_id': rel_type,
        'right_identifier_id': right_id,
        'relationship_comment': ''
    }
    self.db.relationships.insert(**relationship_params)
    self.db.flush()

# def _view_fetch_by_docid(self, view_name, doc_id):
#     return (
#         self.views[view_name]
#         .filter(self.views[view_name].document_id == doc_id)
#         .all()
#         )

# def autocreate_relationships(self, doc_id):
#     view_names = [
#         'v_auto_contains',
#         'v_auto_contained_by',
#         'v_auto_describes',
#         'v_auto_described_by'
#         ]
#     for view_name in view_names:
#         rows = self._view_fetch_by_docid(view_name, doc_id)
#         for row in rows:
#             self.create_relationship(
#                 row.left_identifier_id,
#                 row.relationship_type_id,
#                 row.right_identifier_id
#                 )
#     self.db.flush()

# must rewrite
def create_document(self, package_id, name=None, comment=None):
    package = self.db.packages.get(package_id)
    data_license = (
        self.db.licenses
        .filter(self.db.licenses.short_name == 'CC0-1.0')
        .one()
        )
    doc_name = name or package.name
    doc_namespace = self.create_document_namespace(doc_name)
    document_params = {
        'data_license_id': data_license.license_id,
        'spdx_version': 'SPDX-2.0',
        'name': doc_name,
        'document_namespace_id': doc_namespace.document_namespace_id,
        'license_list_version': '2.0',  # TODO: dynamically fill from database table
        'creator_comment': name or '',
        'document_comment': comment or '',
        'package_id': package_id
        }
    new_document = self.db.documents.insert(**document_params)
    self.db.flush()
    # default_creator_id should always be 1, because the default is
    # always the first creator row created.
    # TODO: don't hardcode this.
    default_creator_id = 1
    document_creator_params = {
        'document_id': new_document.document_id,
        'creator_id': default_creator_id
        }
    self.db.documents_creators.insert(**document_creator_params)
    document_identifier_params = {
        'document_namespace_id': doc_namespace.document_namespace_id,
        'document_id': new_document.document_id,
        'id_string': 'SPDXRef-DOCUMENT'
        }
    # create all identifiers
    document_identifier = self.db.identifiers.insert(**document_identifier_params)
    self.db.flush()
    doc_namespace_id = doc_namespace.document_namespace_id
    doc_identifier_id = document_identifier.identifier_id
    describes_ids = self.create_all_identifiers(doc_namespace_id, package_id)
    self.db.flush()
    # create known relationships
    # self.autocreate_relationships(new_document.document_id)
    self.db.flush()
    return new_document

# must rewrite
def fetch(self, table_name, id):
    return getattr(self.db, table_name).get(id)
