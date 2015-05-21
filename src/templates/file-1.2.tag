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
