SPDXVersion: SPDX-1.2
DataLicense: CC0-1.0
Document Comment: <text>{{ document_comment }}</text>

## Creation Information

Creator: {{ creator }}
Created: {{ created }}
CreatorComment: <text>{{ creator_comment }}</text>
LicenseListVersion: {{ license_list_version }}


## Package Information

PackageName: {{ package.name }}
PackageVersion: {{ package.version }}
PackageFileName: {{ package.file_name }}
PackageSupplier: {{ package.supplier}}
PackageOriginator: {{ package.originator }}
PackageDownloadLocation: {{ package.download_location }}
PackageVerificationCode: {{ package.verification_code }}
PackageChecksum: {{ package.checksum }}
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

## File Information

{% for file in files %}
FileName: {{ file.name }}
FileType: {{ file.type }}
FileChecksum: {{ file.checksum }}
LicenseConcluded: {{ file.license_concluded }}
{% for li in file.license_info %}
LicenseInfoInFile: {{ li }}
{% endfor %}
LicenseComments: <text>{{ file.license_comments }}</text>
FileCopyrightText: <text>{{ file.copyright_text }}</text>
FileComment: <text>{{ file.comment }}</text>
FileNotice: <text>{{ file.notice }}</text>
{% endfor %}

## License Information

{% for license in licenses %}
LicenseID: {{ license.id }}
LicenseName: {{ license.name }}
ExtractedText: {{ license.extracted_text }}
LicenseCrossReference: {{ license.cross_reference }}
LicenseComment: <text>{{ license.comment }}</text>
{% endfor %}

{% if reviews %}
## Review Information
{% for review in reviews %}
Reviewer: {{ review.reviewer }}
ReviewDate: {{ review.date }}
ReviewComment: <text>{{ review.comment }}</text>
{% endfor %}
{% endif %}
