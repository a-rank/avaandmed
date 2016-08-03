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


#: com.liferay.portlet.asset.service.AssetEntryServiceUtil#getEntries
def get_asset_entries_by_category(url, username, password, category_id, start, end):
    parameters = "+entryQuery/entryQuery.allCategoryIds/{id}".format(id=category_id)
    paging = "entryQuery.start/{start}/entryQuery.end/{end}".format(start=start, end=end)
    url = "{base_url}/assetentry/get-entries/{parameters}/{paging}".format(base_url=url,
                                                                           parameters=parameters, paging=paging)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.json()


#: com.liferay.portlet.asset.service.AssetEntryServiceUtil#getEntries
def get_asset_entries_by_class(url, username, password, class_name, start, end):
    parameters = "+entryQuery/entryQuery.allCategoryIds/{id}".format(id=class_name)
    paging = "entryQuery.start/{start}/entryQuery.end/{end}".format(start=start, end=end)
    url = "{base_url}/assetentry/get-entries/{parameters}/{paging}".format(base_url=url,
                                                                           parameters=parameters, paging=paging)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.json()


#: com.liferay.portlet.asset.service.AssetEntryServiceUtil#getEntries
def get_linked_asset_entries(url, username, password, entry_id, start, end):
    parameters = "+entryQuery/entryQuery.linkedAssetEntryId/{id}".format(id=entry_id)
    paging = "entryQuery.start/{start}/entryQuery.end/{end}".format(start=start, end=end)
    url = "{base_url}/assetentry/get-entries/{parameters}/{paging}".format(base_url=url,
                                                                           parameters=parameters, paging=paging)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.json()


#: com.liferay.portlet.asset.service.AssetEntryServiceUtil#getEntry
def get_asset_entry(url, username, password, entry_id):
    parameters = "+entryQuery/entryId//{id}/".format(id=entry_id)
    url = "{base_url}/assetentry/get-entry/{parameters}".format(base_url=url,
                                                                parameters=parameters)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.text()


#: com.liferay.portlet.asset.service.AssetEntryServiceUtil#getEntriesCount
def get_asset_entries_count(url, username, password, category_id):
    parameters = "+entryQuery/entryQuery.allCategoryIds/{id}/".format(id=category_id)
    url = "{base_url}/assetentry/get-entries-count/{parameters}".format(base_url=url,
                                                                        parameters=parameters)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.text()


#: com.liferay.portlet.journal.service.JournalArticleServiceUtil#getLatestArticle
def get_latest_article(url, username, password, resource_prim_key):
    parameters = "resource-prim-key/{id}".format(id=resource_prim_key)
    url = "{base_url}/journalarticle/get-latest-article/{parameters}".format(base_url=url,
                                                                             parameters=parameters)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.json()


#: com.liferay.portlet.journal.service.JournalArticleServiceUtil#getArticle
def get_article(url, username, password, group_id, article_id):
    parameters = "group-id/{group_id}/article-id/{article_id}".format(group_id=group_id, article_id=article_id)
    url = "{base_url}/journalarticle/get-article/{parameters}".format(base_url=url,
                                                                      parameters=parameters)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.json()


#: com.liferay.portlet.documentlibrary.service.DLAppServiceUtil#getGroupFileEntries
def get_group_file_entries(url, username, password, group_id, start, end, user_id=0):
    parameters = "group-id/{id}/user-id/{user_id}".format(id=group_id, user_id=user_id)
    paging = "start/{start}/end/{end}".format(start=start, end=end)
    url = "{base_url}/dlapp/get-group-file-entries/{parameters}/{paging}".format(base_url=url,
                                                                                 parameters=parameters,
                                                                                 paging=paging)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.json()


#: com.liferay.portlet.documentlibrary.service.DLAppServiceUtil#getFileEntry
def get_file_entry(url, username, password, file_entry_id):
    parameters = "file-entry-id/{file_entry_id}".format(file_entry_id=file_entry_id)
    url = "{base_url}/dlapp/get-file-entry/{parameters}".format(base_url=url,
                                                                parameters=parameters)
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.json()


#: com.liferay.portal.service.PortalServiceUtil#getBuildNumber
def get_build_number(url, username, password, ):
    url = "{_base_url}/portal/get-build-number"
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    return response.text()
