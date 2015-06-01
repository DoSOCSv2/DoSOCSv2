SPDXVersion: SPDX-1.2
DataLicense: CC0-1.0
DocumentNamespace: {{ document.document_namespace }}
DocumentName: {{ document.name }}
SPDXID: SPDXRef-DOCUMENT
DocumentComment: <text>{{ document.document_comment }}</text>

## External Document References
{% for er in external_refs %}
ExternalDocumentRef: {{ er.id_string }} {{ er.external_uri }} SHA1: {{ er.sha1 }}
{% endfor %}


## Creation Information
{% for creator in creators %}
Creator: {{ creator.creator_type }}: {{ creator.creator_name }} {{ creator.creator_email }}
{% endfor %}
Created: {{ document.created_ts }}
CreatorComment: <text>{{ document.creator_comment }}</text>
LicenseListVersion: {{ document.license_list_version }}


## Document Annotations
{% for annotation in document.annotations %}
Annotator: {{ annotation.creator_type }}: {{ annotation.creator_name }} {{ annotation.creator_email }}
AnnotationDate: {{ annotation.created_ts }}
AnnotationComment: <text>{{ annotation.comment }}</text>
SPDXID: {{ annotation.identifier }}
{% endfor %}


## Document Relationships
{% for relationship in document.relationships %}
Relationship: {{ relationship.left_identifier }} {{ relationship.type }} {{ relationship.right_identifier}}
{% endfor %}


## Package Information

PackageName: {{ package.name }}
SPDXID: {{ package.identifier }}
PackageVersion: {{ package.version }}
PackageFileName: {{ package.file_name }}
PackageSupplier: {{ package.supplier}}
PackageOriginator: {{ package.originator }}
PackageDownloadLocation: {{ package.download_location }}
PackageVerificationCode: {{ package.verification_code }}
PackageChecksum: SHA1: {{ package.checksum }}
PackageHomePage: {{ package.home_page }}
PackageSourceInfo: {{ package.source_info }}
PackageLicenseConcluded: {{ package.license_concluded }}
{% for li in package.license_info_from_files %}
PackageLicenseInfoFromFiles: {{ li }}
{% endfor %}
PackageLicenseDeclared: {{ package.license_declared }}
PackageLicenseComments: <text>{{ package.license_comments }}</text>
PackageCopyrightText: <text>{{ package.copyright_text }}</text>
PackageSummary: <text>{{ package.summary }}</text>
PackageDescription: <text>{{ package.description }}</text>

{% if package.annotations %}
## Annotations
{% for annotation in package.annotations %}
Annotator: {{ annotation.creator_type }}: {{ annotation.creator_name }} {{ annotation.creator_email }}
AnnotationDate: {{ annotation.created_ts }}
AnnotationComment: <text>{{ annotation.comment }}</text>
SPDXID: {{ annotation.identifier }}
{% endfor %}
{% endif %}

{% if package.relationships %}
## Relationships
{% for relationship in package.relationships %}
Relationship: {{ relationship.left_identifier }} {{ relationship.type }} {{ relationship.right_identifier}}
{% endfor %}
{% endif %}


## File Information

{% for file in files %}
FileName: {{ file.name }}
SPDXID: {{ file.identifier }}
FileType: {{ file.type }}
FileChecksum: SHA1: {{ file.checksum }}
LicenseConcluded: {{ file.license_concluded }}
{% for li in file.license_info %}
LicenseInfoInFile: {{ li }}
{% endfor %}
LicenseComments: <text>{{ file.license_comments }}</text>
FileCopyrightText: <text>{{ file.copyright_text }}</text>
{% if file.project %}
ArtifactOfProjectName: {{ file.project.name }}
ArtifactOfProjectHomePage: {{ file.project.homepage }}
ArtifactOfProjectURI: {{ file.project.uri }}
{% endif %}
FileComment: <text>{{ file.comment }}</text>
FileNotice: <text>{{ file.notice }}</text>
{% for contributor in file.contributors %}
FileContributor: {{ contributor.contributor }}
{% endfor %}
{% if file.relationships %}
## Relationships
{% for relationship in package.relationships %}
Relationship: {{ relationship.left_identifier }} {{ relationship.type }} {{ relationship.right_identifier}}
{% endfor %}
{% endif %}
{% endfor %}

## License Information
{% for license in licenses %}
LicenseID: {{ license.id }}
LicenseName: {{ license.name }}
ExtractedText: {{ license.extracted_text }}
LicenseCrossReference: {{ license.cross_reference }}
LicenseComment: <text>{{ license.comment }}</text>
{% endfor %}
