# -*- coding: utf-8 -*-

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

import io

from flask_script import Manager
from app.context import Doku
from app import db
from mysql.connector import Error, IntegrityError
from datetime import datetime

manager = Manager(usage="Perform database operations", description="")


@manager.command
def test():
    "Initiate a test connection to database"
    app = manager.parent.app
    with app.app_context():
        try:
            connection = db.connection
            connection.ping(reconnect=False, attempts=1, delay=0)
            print("Using C extension: {}".format(db.have_cext))
            print("Connected to {host} at {port}. Server version: {info}".format(host=connection.server_host,
                                                                                 port=connection.server_port,
                                                                                 info=connection.get_server_info()))
        except Error as err:
            print("Failure errno:{}, {}".format(err.errno, err.msg))


@manager.command
def create():
    "Create database"
    tables = {}
    tables["coordinate"] = (
        "CREATE TABLE IF NOT EXISTS `coordinate` ("
        "  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,"
        "  `cadastral_number` varchar(14) NOT NULL DEFAULT '',"
        "  `coordinate` point NOT NULL,"
        "  PRIMARY KEY (`id`),"
        "  UNIQUE KEY `cadastral_number_idx` (`cadastral_number`),"
        "  SPATIAL KEY `coordinate_idx` (`coordinate`)"
        ") ENGINE=MyISAM DEFAULT CHARSET=utf8;"
    )

    tables["document"] = (
        "CREATE TABLE IF NOT EXISTS `document` ("
        "  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,"
        "  `item_id` int(11) unsigned NOT NULL,"
        "  `topic_id` int(11) unsigned NOT NULL,"
        "  `item_file_id` int(11) unsigned NOT NULL,"
        "  `title` text  NOT NULL,"
        "  `document_date` datetime DEFAULT NULL,"
        "  `import_date` datetime NOT NULL DEFAULT NOW(),"
        "  `contents` mediumtext  NOT NULL,"
        "  PRIMARY KEY (`id`),"
        "  UNIQUE KEY `item_id_idx` (`item_id`),"
        "  KEY `topic_id_idx` (`topic_id`)"
        ") ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;"
    )

    tables["import"] = (
        "CREATE TABLE IF NOT EXISTS `import` ("
        "  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,"
        "  `imported` int(11) NOT NULL,"
        "  `item_id` int(11) NOT NULL,"
        "  `date` datetime NOT NULL DEFAULT NOW(),"
        "  `result` tinyint(1) NOT NULL DEFAULT '0',"
        "  `description` text,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=MyISAM DEFAULT CHARSET=utf8;"
    )

    tables["locations"] = (
        "CREATE TABLE IF NOT EXISTS `locations` ("
        "  `document_id` int(11) unsigned NOT NULL,"
        "  `coordinate_id` int(11) unsigned NOT NULL,"
        "  PRIMARY KEY (`document_id`,`coordinate_id`)"
        ") ENGINE=MyISAM DEFAULT CHARSET=utf8;"
    )

    tables["topic"] = (
        "CREATE TABLE IF NOT EXISTS `topic` ("
        "  `id` int(11) unsigned NOT NULL,"
        "  `title` varchar(255) NOT NULL DEFAULT '',"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=MyISAM DEFAULT CHARSET=utf8;"
    )

    app = manager.parent.app
    db_name = app.config["MYSQL_DB"]

    app.config["MYSQL_DB"] = ""
    with app.app_context():
        connection = db.connection
        cursor = connection.cursor()
        try:
            print("Creating database {db}".format(db=db_name))
            cursor.execute("CREATE DATABASE IF NOT EXISTS {db} DEFAULT CHARACTER SET 'utf8'".format(db=db_name))
        except Error:
            print("Failed creating database: {}".format(Error))
        cursor.close()

    app.config["MYSQL_DB"] = db_name
    with app.app_context():
        connection = db.connection
        cursor = connection.cursor()
        for table, sql in tables.items():
            print("Creating table {table}".format(table=table))
            try:
                cursor.execute(sql)
            except Error:
                print("Failed creating table: {}".format(Error))

        cursor.execute("INSERT INTO `topic` (`id`, `title`) VALUES"
                       "	(5059,'Planeerimine ja ehitus'),"
                       "	(50285,'Detailplaneeringute algatamine'),"
                       "	(50286,'Detailplaneeringute kehtestamine'),"
                       "	(50287,'Detailplaneeringute vastuvõtmine'),"
                       "	(50288,'Projekteerimistingimuste määramine'),"
                       "	(50344,'Maakorraldus');")

        connection.commit()
        cursor.close()


def downloaded_callback(id, files):
    print("Downloaded {id}".format(id=id))


@manager.command
def fetch():
    "Import documents from amphora"
    app = manager.parent.app
    doku = Doku(amphora_location=app.config["AMPHORA_LOCATION"],
                temp_dir=app.config["TEMP_DIR"])

    # 269660
    id_stop_at = 269660,
    downloaded = doku.download_documents(topic_filter=app.config["AMPHORA_TOPICS"],
                                         delay=5,
                                         extract_text=True,
                                         callback=downloaded_callback)

    sql_document = ("INSERT INTO `document`"
                    " (`item_id`, `topic_id`, `item_file_id`, `title`, `document_date`, `contents`)"
                    " VALUES (?, ?, ?, ?, ?, ?)")

    sql_coordinate = ("INSERT INTO `coordinate`"
                      " (`cadastral_number`, `coordinate`)"
                      " VALUES (%s, ST_PointFromText('POINT(%s %s)'))")

    sql_locations = ("INSERT INTO `locations`"
                     " (`document_id`, `coordinate_id`)"
                     " VALUES (?, ?)")

    sql_import = ("INSERT INTO `import`"
                  " (`imported`, `item_id`, `result`, `description`)"
                  " VALUES (?, ?, ?, ?)")

    connection = db.connection
    prepared_cursor_document = connection.cursor(prepared=True)
    prepared_cursor_locations = connection.cursor(prepared=True)
    prepared_cursor_import = connection.cursor(prepared=True)
    cursor_coordinate = connection.cursor()

    first_item_id = 0
    if len(downloaded):
        first_item_id = downloaded.keys()[0]

    for item_id, document in downloaded.items():
        cadastrals = document["cadastral"]
        if len(cadastrals):
            file_id, topic_id, title, date = document["data"]
            mysql_date = datetime.strptime(date[:-1], "%Y-%m-%dT%H:%M:%S")
            with io.open(document["text"], "r", encoding="utf8") as f:
                prepared_cursor_document.execute(sql_document,
                                                 (item_id, topic_id, file_id, title, mysql_date, f.read()))
            document_id = prepared_cursor_document.lastrowid
            for number in cadastrals:
                geo = doku.geocode_cadastral(number)
                try:
                    cursor_coordinate.execute(sql_coordinate, (number, geo.get("lon"), geo.get("lat")))
                except IntegrityError:
                    continue
                coordinate_id = cursor_coordinate.lastrowid
                prepared_cursor_locations.execute(sql_locations, (document_id, coordinate_id))

    prepared_cursor_import.execute(sql_import, (len(downloaded), first_item_id, True, ""))

    connection.commit()
    prepared_cursor_document.close()
    prepared_cursor_locations.close()
    prepared_cursor_import.close()
    cursor_coordinate.close()
