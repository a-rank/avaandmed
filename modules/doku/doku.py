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
import fulltext
from os import path as os_path
from ijson import parse as ijson_parse
from collections import defaultdict, OrderedDict
from operator import setitem
from time import sleep
from cgi import parse_header


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

    def create_file_url(self, item_id, item_file_id):
        return "{amphora_url}/?itm={itm}&af={af}".format(amphora_url=self.amphora_url,
                                                         itm=item_id, af=item_file_id)

    def extract_text_to_file(self, filename, filename_txt=None):
        if not filename_txt:
            filename_txt = "".join([filename, ".txt"])
        text = fulltext.get(filename)
        with open(filename_txt, "w") as f:
            f.write(text)
        return filename_txt

    def download_file(self, url, filename, block_size=1024, timeout=20, extension_from_header=False):
        response = requests.get(url, stream=True, timeout=timeout)
        if response.ok:
            if extension_from_header:
                _, params = parse_header(response.headers.get("content-disposition", ""))
                _, extension = os_path.splitext(params["filename"])
                if not extension:
                    extension = ".doc"
                filename = "".join([filename, extension])
            with open(filename, "w") as f:
                for block in response.iter_content(block_size):
                    f.write(block)
            return filename
        else:
            raise DownloadError(response.status_code, url)

    def download_file_list(self, filter_topic_ids):
        filepath = os_path.join(self.temp_dir, "act.json")
        self.download_file(self.amphora_api_url, filepath)

        files = OrderedDict()
        ids = defaultdict(int)
        setters = {
            "Acts.item.topic_id.number": lambda ids, value: setitem(ids, "topic_id", value),
            "Acts.item.item_id.number": lambda ids, value: setitem(ids, "item_id", value),
            "Acts.item.item_file_id.number": lambda ids, value: setitem(ids, "item_file_id", value),
            "Acts.item.end_map": lambda ids, value: ids.clear()
        }

        with open(filepath, "r") as f:
            parser = ijson_parse(f)
            for prefix, event, value in parser:
                if (prefix, event) == ("Acts.item", "end_map"):
                    if ids["topic_id"] in filter_topic_ids and ids["item_id"] and ids["item_file_id"]:
                        files[str(ids["item_id"])] = self.create_file_url(ids["item_id"], ids["item_file_id"])

                setter = setters.get("".join([prefix, ".", event]))
                if setter:
                    setter(ids, value)

        return files

    def download_files(self, file_list, delay=None, extract_text=False, callback=None):
        downloaded_files = {}
        for item_id, url in file_list.items():
            filename = os_path.join(self.temp_dir, item_id)
            downloaded_file = self.download_file(url, filename, extension_from_header=True)
            downloaded_files[item_id] = {"file": downloaded_file}

            if extract_text:
                downloaded_files[item_id]["text"] = self.extract_text_to_file(downloaded_file)

            if callback:
                callback(downloaded_files[item_id])

            if delay:
                sleep(delay)

        return downloaded_files
