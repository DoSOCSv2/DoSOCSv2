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

## External Document References
{% for er in external_refs %}
ExternalDocumentRef: {{ er.id_string }} {{ er.uri }} SHA1: {{ er.sha1 }}
{% endfor %}


## Creation Information
{% for creator in document.creators %}
Creator: {{ creator.creator }}
{% endfor %}
Created: {{ document.created_ts | utctimestamp }}
CreatorComment: {{ document.creator_comment | text }}
LicenseListVersion: {{ document.license_list_version }}


## Document Annotations
{% for annotation in document.annotations %}
Annotator: {{ annotation.creator }}
AnnotationDate: {{ annotation.created_ts | utctimestamp }}
AnnotationComment: {{ annotation.comment | text }}
AnnotationType: {{ annotation.type }}
SPDXID: {{ annotation.id_string }}
{% endfor %}


{% if document.relationships != None %}
## Document Relationships
{% for relationship in document.relationships %}
Relationship: {{ relationship.left_id_string }} {{ relationship.type }} {{ relationship.right_id_string }}
    {% if relationship.comment %}
RelationshipComment: {{ relationship.comment | text }}
    {% endif %}
{% endfor %}
{% endif %}

## Package Information

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

{% if package.annotations %}
## Annotations
{% for annotation in package.annotations %}
Annotator: {{ annotation.creator }}
AnnotationDate: {{ annotation.created_ts }}
AnnotationComment: {{ annotation.comment | text }}
AnnotationType: {{ annotation.type }}
SPDXID: {{ annotation.id_string }}
{% endfor %}
{% endif %}

{% if package.relationships != None %}
## Relationships
{% for relationship in package.relationships %}
Relationship: {{ relationship.left_id_string }} {{ relationship.type }} {{ relationship.right_id_string }}
{% endfor %}
{% endif %}


## File Information
{% for file in package.files %}


FileName: {{ file.name }}
SPDXID: {{ file.id_string }}
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
    {% if file.annotations %}
## Annotations
        {% for annotation in file.annotations %}
Annotator: {{ annotation.creator }}
AnnotationDate: {{ annotation.created_ts }}
AnnotationComment: {{ annotation.comment | text }}
AnnotationType: {{ annotation.type }}
SPDXID: {{ annotation.id_string }}
        {% endfor %}
    {% endif %}
    {% if file.relationships != None %}
## Relationships
        {% for relationship in file.relationships %}
Relationship: {{ relationship.left_id_string }} {{ relationship.type }} {{ relationship.right_id_string }}
        {% endfor %}
    {% endif %}
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
