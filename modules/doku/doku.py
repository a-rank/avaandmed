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
from os import path as os_path
from ijson import parse as ijson_parse
from collections import defaultdict
from operator import setitem


class DownloadError(Exception):
    def __init__(self, response_code, file_url):
        Exception.__init__(self)
        self.response_code = response_code
        self.file_url = file_url


class Doku(object):
    def __init__(self, amphora_location, temp_dir):
        if not amphora_location:
            raise ValueError
        else:
            self.amphora_url = "http://atp.amphora.ee/{location}".format(location=amphora_location)
            self.amphora_api_url = "{amphora_url}/api/act".format(amphora_url=self.amphora_url)

        if not temp_dir:
            raise ValueError
        else:
            self.temp_dir = temp_dir

    def download_file(self, file_url, output_path, block_size=1024, timeout=20):
        response = requests.get(file_url, stream=True, timeout=timeout)
        if response.ok:
            with open(output_path, "w") as downloaded_file:
                for block in response.iter_content(block_size):
                    downloaded_file.write(block)
            return response.headers.get("content-length", 0)
        else:
            raise DownloadError(response.status_code, file_url)

    def create_file_url(self, item_id, item_file_id):
        return "{amphora_url}/?itm={itm}&af={af}".format(amphora_url=self.amphora_url,
                                                         itm=item_id, af=item_file_id)

    def download_file_list(self, filter_topic_ids):
        output_path = os_path.join(self.temp_dir, "act.json")
        self.download_file(self.amphora_api_url, output_path)

        files = []
        ids = defaultdict(int)
        setters = {
            "Acts.item.topic_id.number": lambda ids, value: setitem(ids, "topic_id", value),
            "Acts.item.item_id.number": lambda ids, value: setitem(ids, "item_id", value),
            "Acts.item.item_file_id.number": lambda ids, value: setitem(ids, "item_file_id", value),
            "Acts.item.end_map": lambda ids, value: ids.clear()
        }

        with open(output_path, "r") as json:
            parser = ijson_parse(json)
            for prefix, event, value in parser:
                if (prefix, event) == ("Acts.item", "end_map"):
                    if ids["topic_id"] in filter_topic_ids and ids["item_id"] and ids["item_file_id"]:
                        files.append((ids["item_id"], self.create_file_url(ids["item_id"], ids["item_file_id"])))

                setter = setters.get("".join([prefix, ".", event]))
                if setter:
                    setter(ids, value)

        return files
