# Copyright 2016 Allan Rank
#
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

from . import db
from flask import url_for


class Document:
    def __init__(self, result):
        if not isinstance(result, dict):
            raise TypeError
        self.result = result

    def __repr__(self):
        return '<Document {}>'.format(0)

    def to_json(self):
        id = self.result.get("id", 0)
        return {
            "id": id,
            "url": url_for("api.get_document", id=id, _external=True),
            "topic": self.result.get("topic_title", ""),
            "title": self.result.get("title", ""),
            "document_date": self.result.get("document_date", ""),
        }


def fetch_documents(start, page):
    documents = []
    connection = db.connection
    sql = (
        "SELECT d.id, d.item_id,"
        " d.item_file_id, d.title, DATE_FORMAT(d.document_date,'%Y-%m-%dT%TZ') as document_date,"
        " t.id as topic_id, t.title as topic_title,"
        " DATE_FORMAT(d.import_date,'%Y-%m-%dT%TZ') as import_date"
        " FROM document as d"
        " LEFT JOIN topic as t ON d.topic_id = t.id"
        " ORDER BY d.id ASC LIMIT {start}, {page}".format(start=start, page=page))
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    documents = [Document(result) for result in cursor]
    cursor.close()
    return documents
