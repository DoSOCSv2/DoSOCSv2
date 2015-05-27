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

'''Reviewer information in the SPDX object.'''
import MySQLdb

class Review:
    def __init__(self):
        self.reviewer = None
        self.review_date = None
        self.review_comment = None

    @classmethod
    def from_database(self, connection_info, reviewer_id):
        with MySQLDB.connect(**connection_info) as cursor:
            query = """SELECT * FROM reviewers WHERE id = ?"""
            cursor.execute(query, (reviewer_id,))

            result = dbCursor.fetchone()
            inst = cls()
            self.reviewer = result.reviewer
            self.review_date = result.reviewer_date
            self.review_comment = result.reviewer_comment

    def store(self, connection_info, spdx_doc_id):
        # stub
        pass
