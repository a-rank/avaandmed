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

from urlparse import urlparse
import queries
from .article import Article
from .asset import Asset


class Kovtp(object):
    _jsonws_url = None
    _base_url = None
    _jsonws_username = None
    _jsonws_password = None
    _html_parser = "lxml"

    def __init__(self, jsonws_url=None, jsonws_username=None,
                 jsonws_password=None, html_parser=None):
        if jsonws_url is not None:
            self.jsonws_url = jsonws_url
        if jsonws_username is not None:
            self.jsonws_username = jsonws_username
        if jsonws_password is not None:
            self.jsonws_password = jsonws_password
        if html_parser is not None:
            self.html_parser = html_parser

    #: username for liferay's json web service
    @property
    def jsonws_username(self):
        return self._jsonws_username

    @jsonws_username.setter
    def jsonws_username(self, value):
        if value is not None:
            self._jsonws_username = value
        else:
            raise ValueError

    #: password for liferay's json web service
    @property
    def jsonws_password(self):
        return self._jsonws_password

    @jsonws_password.setter
    def jsonws_password(self, value):
        if value is not None:
            self._jsonws_password = value
        else:
            raise ValueError

    #: base url for liferay's json web service
    @property
    def jsonws_url(self):
        return self._jsonws_url

    @jsonws_url.setter
    def jsonws_url(self, value):
        if value is not None:
            self._jsonws_url = value
            result = urlparse(value)
            self._base_url = "".join([result.scheme, "://", result.netloc])
        else:
            raise ValueError

    #: parser for html content
    @property
    def html_parser(self):
        return self._html_parser

    @html_parser.setter
    def html_parser(self, value):
        if value is not None:
            self._html_parser = value
        else:
            raise ValueError

    def get_assets(self, category_id, start, end):
        assets = queries.get_asset_entries_by_category(self._jsonws_url, self._jsonws_username, self._jsonws_password,
                                                       category_id, start, end)
        return [Asset(asset) for asset in assets]

    def get_article(self, group_id, article_id):
        article = queries.get_article(self._jsonws_url, self._jsonws_username, self._jsonws_password, group_id,
                                      article_id)
        return Article(article, self._base_url, self._html_parser)

    def get_latest_article(self, resource_prim_key):
        article = queries.get_latest_article(self._jsonws_url, self._jsonws_username, self._jsonws_password,
                                             resource_prim_key)
        return Article(article, self._base_url, self._html_parser)
