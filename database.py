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

from flask_script import Manager
from app.context import Doku
from app import db
from mysql.connector import Error

manager = Manager(usage="Perform database operations", description="")


@manager.command
def test():
    "Initiate a test connection to database"
    app = manager.parent.app
    with app.app_context():
        try:
            connection = db.connection
            connection.ping(reconnect=False, attempts=1, delay=0)
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
        "  `title` text NOT NULL,"
        "  `document_date` datetime DEFAULT NULL,"
        "  `import_date` datetime NOT NULL DEFAULT NOW(),"
        "  `contents` mediumtext NOT NULL,"
        "  PRIMARY KEY (`id`),"
        "  UNIQUE KEY `item_id_idx` (`item_id`),"
        "  KEY `topic_id_idx` (`topic_id`)"
        ") ENGINE=MyISAM DEFAULT CHARSET=utf8;"
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

    app.config["MYSQL_DB"] = db_name
    with app.app_context():
        connection = db.connection
        cursor = connection.cursor()
        for table, sql in tables.items():
            print("Creating table {table}".format(table=table))
            cursor.execute(sql)

        cursor.execute("INSERT INTO `topic` (`id`, `title`) VALUES"
                       "	(5059,'Planeerimine ja ehitus'),"
                       "	(50285,'Detailplaneeringute algatamine'),"
                       "	(50286,'Detailplaneeringute kehtestamine'),"
                       "	(50287,'Detailplaneeringute vastuvõtmine'),"
                       "	(50288,'Projekteerimistingimuste määramine'),"
                       "	(50344,'Maakorraldus');")
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
    downloaded = doku.download_documents(id_stop_at=269660,
                                         topic_filter=app.config["AMPHORA_TOPICS"],
                                         delay=5,
                                         extract_text=True,
                                         callback=downloaded_callback)

    add_document = ("INSERT INTO `document`"
                    " (`item_id`, `topic_id`, `item_file_id`, `title`, `document_date`, `contents`)"
                    " VALUES (%s, %s, %s, %s, %s, %s)")

    add_coordinate = ("INSERT INTO `coordinate`"
                      " (`cadastral_number`, `coordinate`)"
                      " VALUES (%s, ST_PointFromText('POINT(%s %s)'))")

    add_locations = ("INSERT INTO `locations`"
                     " (`document_id`, `coordinate_id`)"
                     " VALUES (%s, %s)")

    add_import = ("INSERT INTO `import`"
                  " (`imported`, `item_id`, `result`, `description`)"
                  " VALUES (%s, %s, %s, %s)")

    for item_id, document in downloaded.items():
        pass

    print len(downloaded)
