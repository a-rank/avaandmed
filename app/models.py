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

    def __repr__(self):
        return '<Document {}>'.format(0)

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
        if "geojson" in self.result:
            json["geojson"] = self.result["geojson"]
        return json


def fetch_documents(start, page):
    connection = db.connection
    sql = ("SELECT d.id,"
           " d.title, DATE_FORMAT(d.document_date,'%Y-%m-%dT%TZ') as document_date,"
           " t.title as topic"
           " FROM document as d"
           " LEFT JOIN topic as t ON d.topic_id = t.id"
           " ORDER BY d.id ASC LIMIT {start}, {page}".format(start=start, page=page))
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    documents = [Document(result) for result in cursor]
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

    locations_sql = ("SELECT cadastral.number, ST_AsGeoJSON(cadastral.coordinate) as coordinate"
                     " FROM locations"
                     " JOIN cadastral ON cadastral.id = locations.cadastral_id"
                     " WHERE locations.document_id = {id}".format(id=id))
    cursor.execute(locations_sql)
    features = []
    for locations in cursor:
        features.append({
            "type": "Feature",
            "geometry": json.loads(locations["coordinate"]),
            "properties": {"cadastral": locations["number"]}
        })
    result["geojson"] = {
        "type": "FeatureCollection",
        "features": features
    }

    cursor.close()
    return Document(result)
