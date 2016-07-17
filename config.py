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

    JSONWS_URL = "https://www.kuusalu.ee/api/secure/jsonws"
    JSONWS_USERNAME = os.environ.get("JSONWS_USERNAME")
    JSONWS_PASSWORD = os.environ.get("JSONWS_PASSWORD")
    JSONWS_JOBS_CATEGORY_ID = 11510878
    JSONWS_NEWS_CATEGORY_ID = 7619124
    JSONWS_GROUP_ID = 7610268
    JSONWS_COMPANY_ID = 7610243
    JSONWS_BUSSES_ARTICLE_ID = 8461475

    PAGE_SIZE = 50
    HTML_PARSER = "lxml"


class ProdConfig(Config):
    DEBUG = False


class DevConfig(Config):
    DEBUG = True
