#!/usr/bin/env python2

from __future__ import print_function, unicode_literals

import xmltodict
import re
from collections import OrderedDict


def as_list(item):
    if isinstance(item, list):
        return item
    else:
        return [item]


def extract_cpe(item):
    if isinstance(item, OrderedDict):
        return item['#text']
    else:
        return item


def strip_whitespace(s):
    return re.sub(r'(\n|\s+)', r' ', s)


def get_cpes(dep):
    idents = as_list(dep.get('identifiers', {}).get('identifier', []))
    cpes = []
    for ident in idents:
        if ident['@type'] == 'cpe':
            cpes.append({
                'cpe': ident['name'],
                'confidence': ident['@confidence'],
                'url': ident.get('url', '')
                })
    return cpes


def parse_dependency_xml(xml_text):
    x = xmltodict.parse(xml_text)
    deps = []
    for dep in as_list(x['analysis']['dependencies']['dependency']):
        this_vulns = []
        if 'vulnerabilities' in dep:
            for vuln in as_list(dep['vulnerabilities']['vulnerability']):
                v = {
                    'name': vuln['name'],
                    'description': vuln.get('description', ''),
                    'severity': vuln.get('severity', 'N/A'),
                    'cvssScore': vuln.get('cvssScore', '0.0'),
                    #'cpes': [extract_cpe(cpe) for cpe in as_list(vuln['vulnerableSoftware']['software'])]
                    }
                this_vulns.append(v)
        deps.append({
            'sha1': dep['sha1'],
            'vulnerabilities': this_vulns,
            'cpes': get_cpes(dep)
            })
    return deps

if __name__ == '__main__':
    import pprint
    import sys
    pprint.pprint(parse_dependency_xml(sys.stdin.read()))
