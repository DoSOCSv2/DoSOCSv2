#!/usr/bin/python
'''
<SPDX-License-Identifier: Apache-2.0>
Copyright 2014 University of Nebraska at Omaha (UNO)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''Define Reviewer information in the spdx object.'''
import MySQLdb
import datetime
import settings


class reviewerInfo:
    def __init__(self):
        self.reviewer = None
        self.reviewDate = datetime.datetime.now()
        self.reviewComment = None

    def getReviewerInfo(self, reviewer_id, dbCursor):
        '''gets reviewerInfo from database'''
        sqlCommand = """SELECT * FROM reviewers WHERE id = ?"""
        dbCursor.execute(sqlCommand, (reviewer_id))

        queryReturn = dbCursor.fetchone()
        if queryReturn is not None:
            self.reviewer = queryReturn.reviewer
            self.reviewDate = queryReturn.reviewer_date
            self.reviewComment = queryReturn.reviewer_comment

    def insertReviewerInfo(self, spdx_doc_id, dbCursor):
        '''inserts reviewerInfo into database'''
        '''Get id of reviewer'''
        sqlCommand = "SHOW TABLE STATUS LIKE 'reviewers'"
        dbCursor.execute(sqlCommand)
        reviewerId = dbCursor.fetchone()[10]

        sqlCommand = """INSERT INTO reviewers (reviewer,
                                                reviewer_date,
                                                reviewer_comment,
                                                spdx_doc_id,
                                                created_at,
                                                updated_at)
                            VALUES (%s,
                                    %s,
                                    %s,
                                    %s,
                                    CURRENT_TIMESTAMP,
                                    CURRENT_TIMESTAMP)"""
        dbCursor.execute(sqlCommand, (self.reviewer,
                                      self.reviewDate,
                                      self.reviewComment,
                                      spdx_doc_id))

        return reviewerId

    def outputReviewerInfo_TAG(self):
        '''outputs reviewerInfo in tag format'''

        output = None
        if self.reviewer != None:
            output += "Reviewer: " + self.reviewer + '\n'
        if self.reviewer != None and self.reviewDate != None:
            output += "ReviewDate: " + str(self.reviewDate) + '\n'
        if self.reviewComment != None:
            output += "ReviewComment: <text>"
            output += self.reviewComment
            output += "</text>\n"

        return output

    def outputReviewerInfo_RDF(self):
        '''outputs reviewerInfo in rdf format'''
        output = None
        output += '\t\t<reviewer>' + self.reviewer + '</reviewer>\n'
        if self.reviewer != None and self.reviewDate != None:
            output += '\t\t<reviewDate>'
            output += str(self.reviewDate) + '</reviewDate>\n'
        if self.reviewComment != None:
            output += '\t\t<rdfs:comment>'
            output += self.reviewComment
            output += '</rdfs:comment>\n'

        return output

    def outputReviewerInfo_JSON(self):
        '''outputs reviewerInfo in json format'''
        output =  '{\n'
        output += '\t\t\t"reviewer" : "' + str(self.reviewer) + '",\n'
        output += '\t\t\t"reviewDate" : "' + str(self.reviewDate) + '",\n'
        output += '\t\t\t"comment" : "' + str(self.reviewComment) + '"\n'
        output += '\t\t}'

        return output
