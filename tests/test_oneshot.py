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


from .helpers import TempEnv, run_dosocs2
from tempfile import NamedTemporaryFile

TEMP_CONFIG = '''
connection_uri = sqlite:///{0}
namespace_prefix = sqlite:///{0}
scanner_copyright_path = /dev/null
scanner_dependency_check_path = /dev/null
scanner_monk_path = /dev/null
scanner_nomos_path = /dev/null
'''

SHORT_TEMPLATE = '''
SPDXVersion: {{ document.spdx_version }}
DataLicense: {{ document.data_license }}
DocumentName: {{ document.name }}
DocumentComment: {{ document.document_comment | text }}

## Creation Information
{% for creator in document.creators %}
Creator: {{ creator.creator }}
{% endfor %}
CreatorComment: {{ document.creator_comment | text }}
LicenseListVersion: {{ document.license_list_version }}


## Package Information

PackageName: {{ package.name }}
{% if package.version %}
PackageVersion: {{ package.version }}
{% endif %}
PackageFileName: {{ package.file_name }}
PackageSupplier: {{ package.supplier | noassertion }}
PackageOriginator: {{ package.originator | noassertion }}
PackageDownloadLocation: {{ package.download_location | noassertion }}
PackageVerificationCode: {{ package.verification_code }}
{% if package.checksum != None %}
PackageChecksum: SHA1: {{ package.checksum }}
{% endif %}
PackageHomePage: {{ package.home_page | noassertion }}
{% if package.source_info %}
PackageSourceInfo: {{ package.source_info }}
{% endif %}
PackageLicenseConcluded: {{ package.license_concluded | noassertion }}
{% for li in package.license_info_from_files %}
PackageLicenseInfoFromFiles: {{ li.license_short_name }}
{% endfor %}
PackageLicenseDeclared: {{ package.license_declared | noassertion }}
PackageLicenseComments: {{ package.license_comments | text }}
PackageCopyrightText: {{ package.copyright_text | text_default }}
PackageSummary: {{ package.summary | text }}
PackageDescription: {{ package.description | text }}
PackageComment: {{ package.comment | text }}

## File Information
{% for file in package.files %}


FileName: {{ file.name }}
FileType: {{ file.type }}
FileChecksum: SHA1: {{ file.checksum }}
LicenseConcluded: {{ file.license_concluded | noassertion }}
    {% for fli in file.license_info %}
LicenseInfoInFile: {{ fli.short_name | noassertion }}
    {% endfor %}
LicenseComments: {{ file.license_comments | text }}
FileCopyrightText: {{ file.copyright_text | text_default }}
    {% if file.project_name %}
ArtifactOfProjectName: {{ file.project_name | noassertion }}
ArtifactOfProjectHomePage: {{ file.project_homepage | noassertion }}
ArtifactOfProjectURI: {{ file.project_uri | noassertion }}
    {% endif %}
FileComment: {{ file.comment | text }}
FileNotice: {{ file.notice | text }}
    {% for contributor in file.contributors %}
FileContributor: {{ contributor.contributor }}
    {% endfor %}

{% endfor %}

{% if licenses %}

## License Information
{% for license in licenses %}

LicenseID: {{ license.id_string }}
LicenseName: {{ license.name }}
ExtractedText: <text>{{ license.extracted_text }}</text>
LicenseCrossReference: {{ license.cross_reference }}
LicenseComment: {{ license.comment | text }}
{% endfor %}
{% endif %}
'''

def test_oneshot_typical_case_returns_zero(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        args = [
            'oneshot', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        assert ret == 0


def test_oneshot_with_package_comment(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        _ = capsys.readouterr()
        args = [
            'oneshot', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '--package-comment=12345',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        out, _ = capsys.readouterr()
        assert 'PackageComment: <text>12345</text>' in out


def test_oneshot_with_package_name(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        _ = capsys.readouterr()
        args = [
            'oneshot', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '--package-name=12345',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        out, _ = capsys.readouterr()
        assert 'PackageName: 12345' in out


def test_oneshot_with_package_version(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        _ = capsys.readouterr()
        args = [
            'oneshot', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '--package-version=12345',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        out, _ = capsys.readouterr()
        assert 'PackageVersion: 12345' in out


def test_oneshot_with_document_comment(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        _ = capsys.readouterr()
        args = [
            'oneshot', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '--doc-comment=12345',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        out, _ = capsys.readouterr()
        assert 'DocumentComment: <text>12345</text>' in out


def test_oneshot_with_document_name(capsys):
    with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
        _ = capsys.readouterr()
        args = [
            'oneshot', 
            '-f',
            temp_config.name,
            '-s',
            'dummy',
            '--doc-name=12345',
            '/dev/null'
            ]
        ret = run_dosocs2(args)
        out, _ = capsys.readouterr()
        assert 'DocumentName: 12345' in out


def test_oneshot_same_document_as_scan_print_generate(capsys):
    with NamedTemporaryFile(mode='w+') as template_file:
        template_file.write(SHORT_TEMPLATE)
        template_file.flush()
        with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
            _ = capsys.readouterr()
            args = [
                'oneshot', 
                '-f',
                temp_config.name,
                '-s',
                'dummy',
                '-T',
                template_file.name,
                '/dev/null'
                ]
            ret = run_dosocs2(args)
            oneshot_out, _ = capsys.readouterr()
        with TempEnv(TEMP_CONFIG) as (temp_config, temp_db):
            _ = capsys.readouterr()
            args = [
                'scan', 
                '-f',
                temp_config.name,
                '-s',
                'dummy',
                '/dev/null'
                ]
            ret = run_dosocs2(args)
            args = [
                'generate', 
                '-f',
                temp_config.name,
                '1'
                ]
            ret = run_dosocs2(args)
            args = [
                'print', 
                '-f',
                temp_config.name,
                '-T',
                template_file.name,
                '1'
                ]
            ret = run_dosocs2(args)
            out, err = capsys.readouterr()
        assert out in oneshot_out
