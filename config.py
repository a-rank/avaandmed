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

import os


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMP_DIR = os.path.join(BASE_DIR, "temp")

    JSONWS_URL = "https://www.kuusalu.ee/api/secure/jsonws"
    JSONWS_USERNAME = os.environ.get("JSONWS_USERNAME")
    JSONWS_PASSWORD = os.environ.get("JSONWS_PASSWORD")
    JSONWS_JOBS_CATEGORY_ID = 11510878
    JSONWS_NEWS_CATEGORY_ID = 7619124
    JSONWS_PLANNINGS_CATEGORY_ID = 10386701
    JSONWS_GROUP_ID = 7610268
    JSONWS_COMPANY_ID = 7610243
    JSONWS_BUSSES_ARTICLE_ID = 8461475

    PORTAL_URL = "https://www.kuusalu.ee"
    HTML_PARSER = "lxml"

    AMPHORA_TOPICS = [5059, 50285, 50286, 50287, 50288, 50344]
    AMPHORA_LOCATION = "kuusaluvv"

    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")


class ProdConfig(Config):
    DEBUG = False
    PAGE_SIZE = 50

    MYSQL_DB = "avaandmed"
    MYSQL_DATABASE_HOST = "localhost"


class DevConfig(Config):
    DEBUG = True
    PAGE_SIZE = 30

    MYSQL_DB = "avaandmed"
    MYSQL_HOST = "localhost"
