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

from .utils import timestamp_to_8601


class Asset:
    def __init__(self, asset):
        if not isinstance(asset, dict):
            raise TypeError
        self.asset = asset

    def get_primary_key(self):
        return self.asset.get("classPK", 0)

    def get_class_uuid(self):
        return self.asset.get("classUuid", "")

    def get_description(self):
        return self.asset.get("description", "")

    def get_entry_id(self):
        return self.asset.get("entryId", 0)

    def get_create_date(self):
        return timestamp_to_8601(self.asset.get("createDate", ""))

    def get_expiration_date(self):
        return timestamp_to_8601(self.asset.get("expirationDate", ""))

    def get_modified_date(self):
        return timestamp_to_8601(self.asset.get("modifiedDate", ""))

    def get_publish_date(self):
        return timestamp_to_8601(self.asset.get("publishDate", ""))

    def get_group_id(self):
        return self.asset.get("groupId", 0)

    def get_mime_type(self):
        return self.asset.get("mimeType", "")

    def get_title(self):
        return self.asset.get("titleCurrentValue", "")

    def get_view_count(self):
        return self.asset.get("viewCount", 0)

    def get_raw(self):
        return self.asset
