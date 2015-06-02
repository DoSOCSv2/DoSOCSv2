SPDXVersion: {{ document.spdx_version }}
DataLicense: {{ document.data_license }}
DocumentNamespace: {{ document.uri }}
DocumentName: {{ document.name }}
SPDXID: {{ document.id_string }}
DocumentComment: <text>{{ document.document_comment }}</text>

## External Document References
{% for er in external_refs %}
ExternalDocumentRef: {{ er.id_string }} {{ er.uri }} SHA1: {{ er.sha1 }}
{% endfor %}


## Creation Information
{% for creator in creators %}
Creator: {{ creator.creator }}
{% endfor %}
Created: {{ document.created_ts }}
CreatorComment: <text>{{ document.creator_comment }}</text>
LicenseListVersion: {{ document.license_list_version }}


## Document Annotations
{% for annotation in document.annotations %}
Annotator: {{ annotation.creator }}
AnnotationDate: {{ annotation.created_ts }}
AnnotationComment: <text>{{ annotation.comment }}</text>
AnnotationType: {{ annotation.type }}
SPDXID: {{ annotation.id_string }}
{% endfor %}


## Document Relationships
{% for relationship in document.relationships %}
Relationship: {{ relationship.left_id_string }} {{ relationship.type }} {{ relationship.right_id_string }}
{% endfor %}


## Package Information

PackageName: {{ package.name }}
SPDXID: {{ package.id_string }}
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
PackageComment: <text>{{ package.comment }}</text>

{% if package.annotations %}
## Annotations
{% for annotation in package.annotations %}
Annotator: {{ annotation.creator }}
AnnotationDate: {{ annotation.created_ts }}
AnnotationComment: <text>{{ annotation.comment }}</text>
AnnotationType: {{ annotation.type }}
SPDXID: {{ annotation.id_string }}
{% endfor %}
{% endif %}

{% if package.relationships %}
## Relationships
{% for relationship in package.relationships %}
Relationship: {{ relationship.left_id_string }} {{ relationship.type }} {{ relationship.right_id_string }}
{% endfor %}
{% endif %}


## File Information

{% for file in files %}
FileName: {{ file.name }}
SPDXID: {{ file.id_string }}
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
{% if file.annotations %}
## Annotations
{% for annotation in file.annotations %}
Annotator: {{ annotation.creator }}
AnnotationDate: {{ annotation.created_ts }}
AnnotationComment: <text>{{ annotation.comment }}</text>
AnnotationType: {{ annotation.type }}
SPDXID: {{ annotation.id_string }}
{% endfor %}
{% endif %}
{% if file.relationships %}
## Relationships
{% for relationship in package.relationships %}
Relationship: {{ relationship.left_id_string }} {{ relationship.type }} {{ relationship.right_id_string }}
{% endfor %}
{% endif %}
{% endfor %}

## License Information
{% for license in licenses %}
LicenseID: {{ license.id_string }}
LicenseName: {{ license.name }}
ExtractedText: {{ license.extracted_text }}
LicenseCrossReference: {{ license.cross_reference }}
LicenseComment: <text>{{ license.comment }}</text>
{% endfor %}
