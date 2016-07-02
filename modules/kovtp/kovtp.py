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


class Kovtp:
    #: base url for liferay's json web service
    jsonws_url = None

    #: username for liferay's json web service
    jsonws_username = None

    #: password for liferay's json web service
    jsonws_password = None

    def __init__(self, jsonws_url=None, jsonws_username=None,
                 jsonws_password=None):
        # type: (object, object, object) -> object
        # type: (object, object, object) -> object
        """

        :rtype: object
        """
        if jsonws_url is not None:
            self.jsonws_url = jsonws_url
        if jsonws_username is not None:
            self.jsonws_username = jsonws_username
        if jsonws_password is not None:
            self.jsonws_password = jsonws_password

    #: com.liferay.portlet.asset.service.AssetEntryServiceUtil#getEntries
    def get_asset_entries(self, category_id, start=0, end=0):
        parameters = "+entryQuery/entryQuery.allCategoryIds/{id}/entryQuery.orderByCol1/createDate".format(
            id=category_id)
        if end and end > start:
            parameters = "{parameters}/entryQuery.start/{start}/entryQuery.end/{end}".format(start=start, end=end,
                                                                                             parameters=parameters)
        url = "{base_url}assetentry/get-entries/{parameters}".format(base_url=self.jsonws_url,
                                                                     parameters=parameters)
        response = requests.get(url, auth=HTTPBasicAuth(self.jsonws_username, self.jsonws_password))
        return response.json()

    #: com.liferay.portlet.asset.service.AssetEntryServiceUtil#getEntriesCount
    def get_asset_entries_count(self, category_id):
        parameters = "+entryQuery/entryQuery.allCategoryIds/{id}/".format(id=category_id)
        url = "{base_url}assetentry/get-entries-count/{parameters}".format(base_url=self.jsonws_url,
                                                                           parameters=parameters)
        response = requests.get(url, auth=HTTPBasicAuth(self.jsonws_username, self.jsonws_password))
        return response.text()

    #: com.liferay.portlet.journal.service.JournalArticleServiceUtil#getLatestArticle
    def get_latest_article(self, resource_prim_key):
        parameters = "resource-prim-key/{id}".format(id=resource_prim_key)
        url = "{base_url}journalarticle/get-latest-article/{parameters}".format(base_url=self.jsonws_url,
                                                                                parameters=parameters)
        response = requests.get(url, auth=HTTPBasicAuth(self.jsonws_username, self.jsonws_password))
        return response.json()

    #: com.liferay.portlet.journal.service.JournalArticleServiceUtil#getArticle
    def get_article(self, group_id, article_id):
        parameters = "group-id/{group_id}/article-id/{article_id}".format(group_id=group_id, article_id=article_id)
        url = "{base_url}journalarticle/get-article/{parameters}".format(base_url=self.jsonws_url,
                                                                         parameters=parameters)
        response = requests.get(url, auth=HTTPBasicAuth(self.jsonws_username, self.jsonws_password))
        return response.json()
