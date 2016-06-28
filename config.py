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
    JSONWS_URL = "https://www.kuusalu.ee/api/secure/jsonws/"
    JSONWS_USERNAME = os.environ.get("JSONWS_USERNAME")
    JSONWS_PASSWORD = os.environ.get("JSONWS_PASSWORD")


class ProdConfig(Config):
    DEBUG = False


class DevConfig(Config):
    DEBUG = True
