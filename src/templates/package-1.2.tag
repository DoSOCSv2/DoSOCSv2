PackageName: {{ package.name }}
PackageVersion: {{ package.version }}
PackageFileName: {{ package.file.name }}
PackageSupplier: {{ package.supplier}}
PackageOriginator: {{ package.originator }}
PackageDownloadLocation: {{ package.download_location }}
PackageVerificationCode: {{ package.verification_code }}
PackageChecksum: {{ package.checksum }}
PackageHomePage: {{ package.home_page }}
PackageSourceInfo: {{ package.source_info }}
PackageLicenseConcluded: {{ package.license_concluded }}
{% for li in package.license_info_from_files }}
PackageLicenseInfoFromFiles: {{ li }}
{% endfor %}
PackageLicenseDeclared: {{ package.license_declared }}
PackageLicenseComments: <text>{{ package.license_comments }}</text>
PackageCopyrightText: <text>{{ package.copyright_text }}</text>
PackageSummary: <text>{{ package.summary }}</text>
PackageDescription: <text>{{ package.description }}</text>
