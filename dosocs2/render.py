# Copyright (C) 2015 University of Nebraska at Omaha
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

import time

import jinja2
from . import queries

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
    return list(sorted(dict(**row) for row in conn.execute(query)))


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
    for file in sorted(package['files']):
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
