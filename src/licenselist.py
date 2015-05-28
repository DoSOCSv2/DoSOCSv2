import re
import sys
import subprocess


def scrape(page_text):
    '''Scrape license info and return (url, name, shortname) tuples'''
    url_part = r'<tr>\s*<td><a href=\"(.*?)\".*?>'
    name_part = r'(.*?)</a></td>\s*.*?'
    shortname_part = r'<code property=\"spdx:licenseId\">(.*?)</code>'
    pattern_str = url_part + name_part + shortname_part
    pattern = re.compile(pattern_str)
    page_one_line = page_text.replace('\n', '')
    rows = pattern.findall(page_one_line)
    return rows

def scrape_site(url='http://spdx.org/licenses/'):
    page_text = subprocess.check_output(['curl', url])
    rows = scrape(page_text)
    # append full url to first column
    completed_rows = [(url + row[0][2:], row[1], row[2])
                      for row in rows
                      ]
    return completed_rows
