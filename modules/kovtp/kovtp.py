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

import requests
from requests.auth import HTTPBasicAuth
import queries


class Kovtp:
    #: base url for liferay's json web service
    jsonws_url = None

    #: username for liferay's json web service
    jsonws_username = None

    #: password for liferay's json web service
    jsonws_password = None

    def __init__(self, jsonws_url=None, jsonws_username=None,
                 jsonws_password=None):
        if jsonws_url is not None:
            self.jsonws_url = jsonws_url
        if jsonws_username is not None:
            self.jsonws_username = jsonws_username
        if jsonws_password is not None:
            self.jsonws_password = jsonws_password

    def get_asset_entries(self, category_id, start, end):
        return queries.get_asset_entries(self.jsonws_url, self.jsonws_username, self.jsonws_password, category_id,
                                         start, end)

    def get_asset_entries_count(self, category_id):
        return queries.get_asset_entries_count(self.jsonws_url, self.jsonws_username, self.jsonws_password, category_id)

    def get_latest_article(self, resource_prim_key):
        return queries.get_latest_article(self.jsonws_url, self.jsonws_username, self.jsonws_password,
                                          resource_prim_key)

    def get_article(self, group_id, article_id):
        return queries.get_article(self.jsonws_url, self.jsonws_username, self.jsonws_password, group_id, article_id)

    def get_group_file_entries(self, group_id, start, end, user_id=0):
        return queries.get_group_file_entries(self.jsonws_url, self.jsonws_username, self.jsonws_password, group_id,
                                              start, end, user_id=0)

    def get_file_entry(self, file_entry_id):
        return queries.get_file_entry(self.jsonws_url, self.jsonws_username, self.jsonws_password, file_entry_id)

    def get_build_number(self):
        return queries.get_build_number(self.jsonws_url, self.jsonws_username, self.jsonws_password)
