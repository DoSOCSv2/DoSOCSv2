# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2014-2015 University of Nebraska at Omaha (UNO) and other
# contributors.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''dosocs2 application settings.'''

'''Paths to external scanner executables.

To define a scanner name and path here is not enough to enable dosocs2 to use
that scanner; it also needs an interface defined for it in scanners.py.
'''

scanner = {
    'nomos': "/usr/share/fossology/nomos/agent/nomos"
}

settings = {
    # 'connection-uri': dbms://user:password@hostname:port/database
    'connection-uri': 'postgresql://spdx:spdx@localhost:5432/spdx',
    'namespace-prefix': 'postgresql://localhost:5432/spdx'
}

# version string used throughout program
VERSION = '0.003'
