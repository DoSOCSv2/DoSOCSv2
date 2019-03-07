{#
Copyright (C) 2015 University of Nebraska at Omaha

This file is part of dosocs2.

dosocs2 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

dosocs2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with dosocs2.  If not, see <http://www.gnu.org/licenses/>.

SPDX-License-Identifier: GPL-2.0+
#}
SPDXVersion: {{ document.spdx_version }}
DataLicense: {{ document.data_license }}
DocumentNamespace: {{ document.uri }}
DocumentName: {{ document.name }}
SPDXID: {{ document.id_string }}
DocumentComment: {{ document.document_comment | text }}
PackageName: {{ package.name }}
SPDXID: {{ package.id_string }}
{% if package.version %}
PackageVersion: {{ package.version }}
{% endif %}
PackageFileName: {{ package.file_name }}
PackageSupplier: {{ package.supplier | noassertion }}
PackageOriginator: {{ package.originator | noassertion }}
PackageDownloadLocation: {{ package.download_location | noassertion }}
PackageVerificationCode: {{ package.verification_code }}
{% if package.checksum != None %}
PackageChecksum: SHA256: {{ package.checksum }}
{% endif %}
PackageHomePage: {{ package.home_page | noassertion }}
{% if package.source_info %}
PackageSourceInfo: {{ package.source_info }}
{% endif %}
PackageLicenseConcluded: {{ package.license_concluded | noassertion }}
PackageLicenseDeclared: {{ package.license_declared | noassertion }}
PackageLicenseComments: {{ package.license_comments | text }}
PackageCopyrightText: {{ package.copyright_text | text_default }}
PackageSummary: {{ package.summary | text }}
PackageDescription: {{ package.description | text }}
PackageComment: {{ package.comment | text }}
{% for li in package.license_info_from_files %}
PackageLicenseInfoFromFiles: {{ li.license_short_name }}
{% endfor %}
