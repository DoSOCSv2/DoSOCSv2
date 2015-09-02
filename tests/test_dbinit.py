from dosocs2 import schema as db
from dosocs2 import dbinit
from mock import patch, Mock

TEST_LICENSE_PAGE_TEXT = '''<tr>
<td><a href="./BSD-2-Clause-FreeBSD.html" rel="rdf:_40">BSD 2-clause FreeBSD License</a></td>
<td about="./BSD-2-Clause-FreeBSD.html" typeof="spdx:License">
<code property="spdx:licenseId">BSD-2-Clause-FreeBSD</code></td>
<td align="center"></td>
<td><a href="./BSD-2-Clause-FreeBSD.html#licenseText">License Text</a></td>
</tr>
<tr>
<td><a href="./BSD-2-Clause-NetBSD.html" rel="rdf:_41">BSD 2-clause NetBSD License</a></td>
<td about="./BSD-2-Clause-NetBSD.html" typeof="spdx:License">
<code property="spdx:licenseId">BSD-2-Clause-NetBSD</code></td>
<td align="center"></td>
<td><a href="./BSD-2-Clause-NetBSD.html#licenseText">License Text</a></td>
</tr>
<tr>
<td><a href="./BSD-3-Clause.html" rel="rdf:_42">BSD 3-clause &quot;New&quot; or &quot;Revised&quot; License</a></td>
<td about="./BSD-3-Clause.html" typeof="spdx:License">
<code property="spdx:licenseId">BSD-3-Clause</code></td>
<td align="center">Y</td>
<td><a href="./BSD-3-Clause.html#licenseText">License Text</a></td>
</tr>
<tr>
<td><a href="./BSD-3-Clause-Clear.html" rel="rdf:_43">BSD 3-clause Clear License</a></td>
<td about="./BSD-3-Clause-Clear.html" typeof="spdx:License">
<code property="spdx:licenseId">BSD-3-Clause-Clear</code></td>
<td align="center"></td>
<td><a href="./BSD-3-Clause-Clear.html#licenseText">License Text</a></td>
</tr>
<tr>
<td><a href="./BSD-4-Clause.html" rel="rdf:_44">BSD 4-clause &quot;Original&quot; or &quot;Old&quot; License</a></td>
<td about="./BSD-4-Clause.html" typeof="spdx:License">
<code property="spdx:licenseId">BSD-4-Clause</code></td>
<td align="center"></td>
<td><a href="./BSD-4-Clause.html#licenseText">License Text</a></td>
</tr>
'''

@patch('dosocs2.dbinit.urllib2.urlopen')
def test_scrape_license_list(mock_urlopen):
    a = Mock()
    a.read.side_effect = [TEST_LICENSE_PAGE_TEXT]
    mock_urlopen.return_value = a
    result = dbinit.scrape_site('https://spdx.org/licenses')
    expected_result = [
        ['BSD-2-Clause-FreeBSD',
         'BSD 2-clause FreeBSD License',
         'https://spdx.org/licenses/BSD-2-Clause-FreeBSD.html'
         ],
        ['BSD-2-Clause-NetBSD',
         'BSD 2-clause NetBSD License',
         'https://spdx.org/licenses/BSD-2-Clause-NetBSD.html'
         ],
        ['BSD-3-Clause',
         'BSD 3-clause "New" or "Revised" License',
         'https://spdx.org/licenses/BSD-3-Clause.html'
         ],
        ['BSD-3-Clause-Clear',
         'BSD 3-clause Clear License',
         'https://spdx.org/licenses/BSD-3-Clause-Clear.html'],
        ['BSD-4-Clause',
         'BSD 4-clause "Original" or "Old" License',
         'https://spdx.org/licenses/BSD-4-Clause.html'
         ]
        ]
    for got, expected in zip(result, expected_result):
        assert got == expected 
