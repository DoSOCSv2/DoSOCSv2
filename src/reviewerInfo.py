#!/usr/bin/python
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
        '''outputs reviewerInfo to stdout'''

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
