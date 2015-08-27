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

import time

import jinja2
from . import config
from . import queries
from . import util


def _filter_text(value):
    return '<text>' + value + '</text>'


def _filter_text_default(value, default_value='NOASSERTION'):
    if value:
        return '<text>' + value + '</text>'
    else:
        return default_value


def _filter_noassertion(value):
    return value if value else 'NOASSERTION'


def _filter_utctimestamp(value):
    return time.strftime('%FT%TZ', value.timetuple())


jinja2_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
jinja2_env.filters['text'] = _filter_text
jinja2_env.filters['text_default'] = _filter_text_default
jinja2_env.filters['noassertion'] = _filter_noassertion
jinja2_env.filters['utctimestamp'] = _filter_utctimestamp


def get_row(conn, query):
    [row] = conn.execute(query).fetchall()
    return dict(**row)


def get_rows(conn, query):
    return [dict(**row) for row in conn.execute(query)]


def render_template(templatefile, context):
    with open(templatefile, 'r') as f:
        s = f.read()
    t = jinja2_env.from_string(s)
    return t.render(context)


def render_document(conn, docid, template_file):
    document = get_row(conn, queries.documents(docid))
    external_refs = get_rows(conn, queries.external_refs(docid))
    document['creators'] = get_rows(conn, queries.documents_creators(docid))
    document['annotations'] = get_rows(conn, queries.annotations(docid, document['id_string']))
    query = queries.relationships(document['document_namespace_id'], document['id_string'])
    document['relationships'] = get_rows(conn, query)
    package = get_row(conn, queries.documents_packages(docid))
    package['license_info_from_files'] = get_rows(conn, queries.packages_all_licenses_in_files(package['package_id'])) or ['NOASSERTION']
    package['annotations'] = get_rows(conn, queries.annotations(docid, package['id_string']))
    query = queries.relationships(document['document_namespace_id'], package['id_string'])
    package['relationships'] = get_rows(conn, query)
    package['files'] = get_rows(conn, queries.documents_files(docid, package['package_id']))
    for file in package['files']:
        file['license_info'] = get_rows(conn, queries.files_licenses(file['file_id']))
        file['contributors'] = get_rows(conn, queries.file_contributors(file['file_id']))
        file['annotations'] = get_rows(conn, queries.annotations(docid, file['id_string']))
        query = queries.relationships(document['document_namespace_id'], file['id_string'])
        file['relationships'] = get_rows(conn, query)
    licenses = get_rows(conn, queries.documents_unofficial_licenses(docid))
    context = {
        'document': document,
        'external_refs': external_refs,
        'package': package,
        'licenses': licenses
        }
    return render_template(template_file, context)
