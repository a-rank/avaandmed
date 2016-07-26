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

import queries
from .article import Article
from .asset import Asset
from .utils import kovtp_property


class Kovtp(object):
    jsonws_username = kovtp_property()
    jsonws_password = kovtp_property()
    html_parser = kovtp_property()
    portal_url = kovtp_property()
    jsonws_url = kovtp_property()

    def __init__(self, jsonws_url=None, portal_url=None, jsonws_username=None,
                 jsonws_password=None, html_parser=None):
        if jsonws_url is not None:
            self.jsonws_url = jsonws_url
        if portal_url is not None:
            self.portal_url = portal_url
        if jsonws_username is not None:
            self.jsonws_username = jsonws_username
        if jsonws_password is not None:
            self.jsonws_password = jsonws_password
        if html_parser is not None:
            self.html_parser = html_parser

    def get_assets(self, category_id, start, end):
        assets = queries.get_asset_entries_by_category(self.jsonws_url, self.jsonws_username, self.jsonws_password,
                                                       category_id, start, end)
        return [Asset(asset) for asset in assets]

    def get_article(self, group_id, article_id):
        article = queries.get_article(self.jsonws_url, self.jsonws_username, self.jsonws_password, group_id,
                                      article_id)
        return Article(article, self.portal_url, self.html_parser)

    def get_latest_article(self, primary_key):
        article = queries.get_latest_article(self.jsonws_url, self.jsonws_username, self.jsonws_password, primary_key)
        return Article(article, self.portal_url, self.html_parser)
