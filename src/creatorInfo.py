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

'''
Defines the creator info section of an spdx object.
'''
import MySQLdb
import datetime
import settings


class creatorInfo:
    def __init__(self,
                 packagePath,
                 creator=None,
                 creatorComment=None,
                 licenseListVersion=None):
        self.creator = creator
        self.created = datetime.datetime.now()
        self.creatorComment = creatorComment
        self.licenseListVersion = licenseListVersion

    def insertCreatorInfo(self, spdx_doc_id, dbCursor):
        '''inserts creatorInfo into the database'''
        creatorId = None

        '''Get next auto incriment value'''
        sqlCommand = "SHOW TABLE STATUS LIKE 'creators'"
        dbCursor.execute(sqlCommand)
        creatorId = dbCursor.fetchone()
        creatorId = creatorId[10]

        '''insert into creators table'''
        sqlCommand = """INSERT INTO creators (    generated_at,
                                                  creator_comments,
                                                  license_list_version,
                                                  spdx_doc_id, creator,
                                                  created_at,
                                                  updated_at)
                        VALUES (CURRENT_TIMESTAMP,
                                %s,
                                %s,
                                %s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""
        dbCursor.execute(sqlCommand, (self.creatorComment,
                                      self.licenseListVersion,
                                      spdx_doc_id,
                                      self.creator)
                                     )

        return creatorId

    def outputCreatorInfo_TAG(self):
        '''Generates creatorInfo output in Tag format.'''
        output = ""
        output += "Creator: " + str(self.creator) + '\n'
        output += "Created: " + str(self.created) + '\n'

        if self.creatorComment != None:
            output += "CreatorComment: " + str(self.creatorComment) + '\n'
        if self.licenseListVersion != None:
            output += "LicenseListVersion: "
            output += str(self.licenseListVersion) + '\n'

        return output

    def outputCreatorInfo_RDF(self):
        output = ""
        output += '\t\t<creator>' + str(self.creator) + '</creator>\n'
        output += '\t\t<created>' + str(self.created) + '</created>\n'

        if self.creatorComment != None:
            output += '\t\t<rdfs:comment>'
            output += str(self.creatorComment)
            output += '</rdfs:comment>\n'
        if self.licenseListVersion != None:
            output += '\t\t<licenseListVersion>'
            output += str(self.licenseListVersion)
            output += '</licenseListVersion>\n'

        return output

    def outputCreatorInfo_JSON(self):
        output =  '{\n'
        output += '\t\t\t"creator": "' + str(self.creator) + '",\n'
        output += '\t\t\t"created": "' + str(self.created) + '",\n'
        output += '\t\t\t"comment": "' + str(self.creatorComment) + '",\n'
        output += '\t\t\t"licenseListVersion": "' + str(self.licenseListVersion) + '"\n'
        output += '\t\t}'
        return output

    def getCreatorInfo(self, creator_id, dbCursor):
        '''generates the creator structure from the database.'''

        '''get creator info'''
        sqlCommand = """SELECT  id AS creator_id,
                                generated_at,
                                creator_comments,
                                license_list_version,
                                spdx_doc_id,
                                creator,
                                created_at,
                                updated_at
                        FROM creators
                        WHERE id = %s"""

        dbCursor.execute(sqlCommand, (creator_id))

        '''Get row of information'''
        creatorRow = dbCursor.fetchone()
        if creatorRow is not None:
            self.creatorComment = creatorRow[2]
            self.licenseListVersion = creatorRow[3]
            self.creator = creatorRow[5]
            self.created = creatorRow[6]
