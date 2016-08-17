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
from app.context import Doku, GeocodeError
from app import db
from mysql.connector import Error, IntegrityError
from datetime import datetime
from collections import OrderedDict

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
    tables = OrderedDict()
    tables["cadastral"] = (
        "CREATE TABLE IF NOT EXISTS `cadastral` ("
        "  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,"
        "  `number` varchar(14) NOT NULL,"
        "  `coordinate` point NOT NULL,"
        "  PRIMARY KEY (`id`),"
        "  UNIQUE KEY `idx_number` (`number`),"
        "  SPATIAL KEY `idx_coordinate` (`coordinate`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
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
        "  `contents` text  NOT NULL,"
        "  PRIMARY KEY (`id`),"
        "  UNIQUE KEY `idx_item_id` (`item_id`),"
        "  KEY `idx_topic_id` (`topic_id`),"
        "  KEY `idx_document_date` (`document_date`),"
        "  FULLTEXT KEY `idx_contents` (`contents`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;"
    )

    tables["import"] = (
        "CREATE TABLE IF NOT EXISTS `import` ("
        "  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,"
        "  `imported` int(11) NOT NULL,"
        "  `item_id` int(11) NOT NULL,"
        "  `date` datetime NOT NULL DEFAULT NOW(),"
        "  `result` tinyint(1) NOT NULL DEFAULT '0',"
        "  `description` text,"
        "  PRIMARY KEY (`id`),"
        "  KEY `idx_item_id` (`item_id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    )

    tables["locations"] = (
        "CREATE TABLE IF NOT EXISTS `locations` ("
        "  `document_id` int(11) unsigned NOT NULL,"
        "  `cadastral_id` int(11) unsigned NOT NULL,"
        "  PRIMARY KEY (`document_id`,`cadastral_id`),"
        "  KEY `idx_cadastral` (`cadastral_id`),"
        "  CONSTRAINT `fk_cadastral` FOREIGN KEY (`cadastral_id`) REFERENCES `cadastral` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,"
        "  CONSTRAINT `fk_document` FOREIGN KEY (`document_id`) REFERENCES `document` (`id`) ON DELETE CASCADE ON UPDATE CASCADE"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    )

    tables["topic"] = (
        "CREATE TABLE IF NOT EXISTS `topic` ("
        "  `id` int(11) unsigned NOT NULL,"
        "  `title` varchar(255) NOT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
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
        except Error as err:
            print("Failed creating database: {}".format(err.msg))
        cursor.close()

    app.config["MYSQL_DB"] = db_name
    with app.app_context():
        connection = db.connection
        cursor = connection.cursor()
        for table, sql in tables.items():
            print("Creating table {table}".format(table=table))
            try:
                cursor.execute(sql)
            except Error as err:
                print("Failed creating table: {}".format(err.msg))

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


def get_textfile_as_utf8(filename):
    with io.open(filename, "r", encoding="utf8") as f:
        return f.read()


def get_last_item_id(connection):
    sql_latest = "SELECT `item_id` FROM `import` ORDER BY `id` DESC LIMIT 1"
    last_item_id = None
    cursor = connection.cursor()
    cursor.execute(sql_latest)
    result = cursor.fetchone()
    if result:
        (last_item_id,) = result
    cursor.close()
    return last_item_id


def geocode_cadastrals(cadastrals, doku):
    result = []
    for number in cadastrals:
        try:
            result.append((number, doku.geocode_cadastral(number)))
        except GeocodeError as err:
            print("Warning: unable to geocode {}".format(err.cadastral_number))
            continue
    return result


@manager.command
def fetch():
    "Import documents from amphora"
    sql_document = ("INSERT INTO `document`"
                    " (`item_id`, `topic_id`, `item_file_id`, `title`, `document_date`, `contents`)"
                    " VALUES (?, ?, ?, ?, ?, ?)")

    sql_cadastral = ("INSERT INTO `cadastral`"
                     " (`number`, `coordinate`)"
                     " VALUES (%s, ST_PointFromText('POINT(%s %s)'))")

    sql_locations = ("INSERT INTO `locations`"
                     " (`document_id`, `cadastral_id`)"
                     " VALUES (?, "
                     "(SELECT `id` from `cadastral` where `number` = ?))")

    sql_import = ("INSERT INTO `import`"
                  " (`imported`, `item_id`, `result`, `description`)"
                  " VALUES (?, ?, ?, ?)")

    app = manager.parent.app
    connection = db.connection
    id_stop_at = get_last_item_id(connection)
    doku = Doku(amphora_location=app.config["AMPHORA_LOCATION"])
    downloaded = doku.download_documents(id_stop_at=id_stop_at, topic_filter=app.config["AMPHORA_TOPICS"],
                                         delay=5, extract_text=True, callback=downloaded_callback,
                                         folder=app.config["TEMP_DIR"])

    prepared_cursor_document = connection.cursor(prepared=True)
    prepared_cursor_locations = connection.cursor(prepared=True)
    prepared_cursor_import = connection.cursor(prepared=True)
    cursor_cadastral = connection.cursor()

    imported = 0
    for item_id in reversed(downloaded):
        print("Processing {}".format(item_id))
        document = downloaded[item_id]
        cadastrals = geocode_cadastrals(document["cadastral"], doku)
        if len(cadastrals):
            file_id, topic_id, title, date = document["data"]
            db_date = datetime.strptime(date[:-1], "%Y-%m-%dT%H:%M:%S")
            text = get_textfile_as_utf8(document["text"])
            try:
                prepared_cursor_document.execute(sql_document,
                                                 (item_id, topic_id, file_id, title, db_date, text))
            except IntegrityError:
                print("Warning: document already exist {}".format(item_id))
                continue

            document_id = prepared_cursor_document.lastrowid
            imported += prepared_cursor_document.rowcount
            for number, geo in cadastrals:
                try:
                    cursor_cadastral.execute(sql_cadastral, (number, geo["lon"], geo["lat"]))
                except IntegrityError:
                    print("Warning: cadastral already exist {}".format(number))
                prepared_cursor_locations.execute(sql_locations, (document_id, number))

    first_item_id = id_stop_at
    if len(downloaded):
        first_item_id = downloaded.keys()[0]

    try:
        prepared_cursor_import.execute(sql_import, (imported, first_item_id, True, ""))
    except Error as err:
        connection.rollback()
        print("Error {}, {}. Changes rollbacked".format(err.errno, err.msg))
    else:
        connection.commit()
        print("Imported {} documents".format(imported))

    prepared_cursor_document.close()
    prepared_cursor_locations.close()
    prepared_cursor_import.close()
    cursor_cadastral.close()
