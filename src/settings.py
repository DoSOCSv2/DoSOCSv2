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

scanner = {
    'nomos': "/usr/share/fossology/nomos/agent/nomos"
}

settings = {
    # 'connection_url': dbms://user:password@hostname:port/database
    'connection_url': 'postgresql://spdx:spdx@localhost:5432/spdx20',
    'creator_string': 'dosocs2-0.0.1-dev',
    'default_namespace_prefix': 'postgresql://localhost:5432/spdx20'
    # 'echo_sql': False
}
