SPDXVersion: SPDX-1.2
DataLicense: CC0-1.0
Document Comment: <text>{{ document_comment }}</text>

## Creation Information

Creator: {{ creator }}
Created: {{ created }}
CreatorComment: <text>{{ creator_comment }}</text>
LicenseListVersion: {{ license_list_version }}


## Package Information

{% include 'package-1.2.tag' %}

## File Information

{% for file in files %}
{% include 'file-1.2.tag' %}
{% endfor %}

## License Information

{% for license in licenses %}
{% include 'license-1.2.tag' %}
{% endfor %}

{% if reviews %}
## Review Information
{% for review in reviews %}
{% include 'review-1.2.tag' %}
{% endfor %}
{% endif %}
