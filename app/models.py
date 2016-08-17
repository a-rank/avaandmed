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
import json

from . import db
from flask import url_for, abort


class Document:
    def __init__(self, result):
        if not isinstance(result, dict):
            raise TypeError
        self.result = result
        self.features = []
        self.add_feature(result)

    def __repr__(self):
        return '<Document {}>'.format(0)

    def add_feature(self, result):
        self.features.append({
            "type": "Feature",
            "geometry": json.loads(result["coordinate"]),
            "properties": {"cadastral": result["number"]}
        })

    def to_json(self):
        id = self.result.get("id", 0)
        json = {
            "id": id,
            "url": url_for("api.get_document", id=id, _external=True),
            "topic": self.result.get("topic", ""),
            "title": self.result.get("title", ""),
            "document_date": self.result.get("document_date", ""),
        }
        if "contents" in self.result:
            json["contents"] = self.result["contents"]
        if len(self.features):
            json["geojson"] = {
                "type": "FeatureCollection",
                "features": self.features
            }
        return json


def fetch_documents(start, page):
    connection = db.connection
    sql = ("SELECT d.id, d.title,"
           " DATE_FORMAT(d.document_date,'%Y-%m-%dT%TZ') as document_date,"
           " t.title as topic,"
           " c.number, ST_AsGeoJSON(c.coordinate) as coordinate"
           " FROM (SELECT id, title, topic_id, document_date FROM document ORDER BY id DESC LIMIT {start}, {page}) AS d"
           " JOIN locations AS l ON l.document_id = d.id"
           " JOIN cadastral AS c ON c.id = l.cadastral_id"
           " LEFT JOIN topic AS t ON d.topic_id = t.id".format(start=start, page=page))
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    id = None
    document = None
    documents = []
    for result in cursor:
        result_id = result.get("id", 0)
        if id != result_id:
            id = result_id
            if document is not None:
                documents.append(document)
            document = Document(result)
        else:
            document.add_feature(result)
    cursor.close()
    return documents


def fetch_document_or_404(id):
    connection = db.connection
    document_sql = ("SELECT d.id,"
                    " d.title, DATE_FORMAT(d.document_date,'%Y-%m-%dT%TZ') as document_date, d.contents,"
                    " t.title as topic"
                    " FROM document as d"
                    " LEFT JOIN topic as t ON d.topic_id = t.id"
                    " WHERE d.id = {id}".format(id=id))
    cursor = connection.cursor(dictionary=True)
    cursor.execute(document_sql)
    result = cursor.fetchone()
    if not result:
        abort(404)

    document = Document(result)
    locations_sql = ("SELECT cadastral.number, ST_AsGeoJSON(cadastral.coordinate) as coordinate"
                     " FROM locations"
                     " JOIN cadastral ON cadastral.id = locations.cadastral_id"
                     " WHERE locations.document_id = {id}".format(id=id))
    cursor.execute(locations_sql)
    for location in cursor:
        document.add_feature(location)
    cursor.close()

    return document
