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
import iso8601

from . import db
from .context import Doku
from .utils import is_float
from flask import url_for, abort, current_app
from collections import OrderedDict


class Document:
    def __init__(self, result):
        if not isinstance(result, dict):
            raise TypeError
        self.features = []
        self.result = result
        self.add_feature(result)
        self.doku = Doku(amphora_location=current_app.config["AMPHORA_LOCATION"])

    def __repr__(self):
        return '<Document {}>'.format(0)

    def add_feature(self, result):
        if "coordinate" in result:
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
        if "item_file_id" and "item_id" in self.result:
            json["file_url"] = self.doku.create_document_url(self.result["item_file_id"],
                                                             self.result["item_id"])
        return json


def get_coordinates_or_400(coordinate):
    try:
        lon, lat = coordinate.split(",", 1)
    except ValueError:
        abort(400)
    else:
        if not is_float(lon) or not is_float(lat):
            abort(400)
        return (lon, lat)


def verify_date_or_400(date):
    try:
        iso8601.parse_date(date)
    except iso8601.ParseError:
        abort(400)


def fetch_documents(start, page, to_date=None, from_date=None,
                    coordinate=None, search=None, distance_km=5):
    filters = []
    order_by = "ORDER BY d.id DESC"
    group_by = ""
    document_sql = ["SELECT d.id, d.title, d.topic_id, d.document_date FROM document as d"]
    connection = db.connection

    if from_date is not None:
        verify_date_or_400(from_date)
        filters.append("d.document_date <= '{filter}'".format(filter=from_date))
        order_by = "ORDER BY d.document_date DESC"
    if to_date is not None:
        verify_date_or_400(to_date)
        filters.append("d.document_date >= '{filter}'".format(filter=to_date))
        order_by = "ORDER BY d.document_date DESC"
    if search is not None:
        filters.append("MATCH(d.contents) AGAINST('{filter}')".format(filter=connection.converter.escape(search)))
        order_by = ""
    if coordinate is not None:
        lon, lat = get_coordinates_or_400(coordinate)
        filters.append("ST_Contains(ST_MakeEnvelope("
                       "Point(({lon}+({km}/111)),({lat}+({km}/111))),"
                       "Point(({lon}-({km}/111)),({lat}-({km}/111)))),"
                       "c.coordinate)".format(lon=float(lon), lat=float(lat), km=distance_km))
        order_by = ("ORDER BY MIN(ST_Distance_Sphere("
                    "Point({lon}, {lat}), c.coordinate)) ASC".format(lon=lon, lat=lat))
        document_sql.append("JOIN locations AS l ON l.document_id = d.id"
                            " JOIN cadastral AS c ON c.id = l.cadastral_id")
        group_by = "GROUP BY d.id"

    if len(filters):
        document_sql.append("WHERE {filters}".format(filters=" AND ".join(filters)))
    if group_by:
        document_sql.append(group_by)
    if order_by:
        document_sql.append(order_by)
    document_sql.append("LIMIT {start}, {page}".format(start=start, page=page))

    sql = ("SELECT d.id, d.title,"
           " DATE_FORMAT(d.document_date,'%Y-%m-%dT%TZ') as document_date,"
           " t.title as topic,"
           " c.number, ST_AsGeoJSON(c.coordinate) as coordinate"
           " FROM ({document_sql}) AS d"
           " JOIN locations AS l ON l.document_id = d.id"
           " JOIN cadastral AS c ON c.id = l.cadastral_id"
           " LEFT JOIN topic AS t ON d.topic_id = t.id".format(document_sql=" ".join(document_sql)))

    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    documents = OrderedDict()
    for result in cursor:
        id = result.get("id", 0)
        if id in documents:
            documents[id].add_feature(result)
        else:
            documents[id] = Document(result)
    cursor.close()
    return documents.values()


def fetch_document_or_404(id):
    connection = db.connection
    sql = ("SELECT d.id, d.title, d.contents, d.item_id, d.item_file_id,"
           " DATE_FORMAT(d.document_date,'%Y-%m-%dT%TZ') as document_date,"
           " t.title as topic,"
           " c.number, ST_AsGeoJSON(c.coordinate) as coordinate"
           " FROM document AS d"
           " JOIN locations AS l ON l.document_id = d.id"
           " JOIN cadastral AS c ON c.id = l.cadastral_id"
           " LEFT JOIN topic AS t ON d.topic_id = t.id"
           " WHERE d.id = {id}".format(id=id))

    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    document = None
    for result in cursor:
        if not document:
            document = Document(result)
        else:
            document.add_feature(result)
    cursor.close()

    if not document:
        abort(404)
    return document
