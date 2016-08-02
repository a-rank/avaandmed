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
from itertools import islice


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

    def create_document_url(self, item_id, item_file_id):
        return "{amphora_url}/?itm={itm}&af={af}".format(amphora_url=self.amphora_url,
                                                         itm=item_id, af=item_file_id)

    def extract_document_text(self, filename, out_filename=None):
        if not out_filename:
            out_filename = "".join([filename, ".txt"])
        _, extension = os_path.splitext(filename)
        type = None
        if not extension in {".doc", ".docx", ".rtf", ".pdf", ".odt"}:
            type = ("application/msword", None)
        text = fulltext.get(filename, type=type)
        with open(out_filename, "w") as f:
            f.write(text)
        return out_filename

    def download_file(self, url, out_filename, block_size=1024,
                      timeout=20, extension_from_header=False):
        response = requests.get(url, stream=True, timeout=timeout)
        if response.ok:
            if extension_from_header:
                _, params = parse_header(response.headers.get("content-disposition", ""))
                _, extension = os_path.splitext(params.get("filename", ""))
                if extension:
                    out_filename = "".join([out_filename, extension])
            with open(out_filename, "w") as f:
                for block in response.iter_content(block_size):
                    f.write(block)
            return out_filename
        else:
            raise DownloadError(response.status_code, url)

    def download_documents_list(self, topic_filter):
        filepath = os_path.join(self.temp_dir, "act.json")
        self.download_file(self.amphora_api_url, filepath)

        files = OrderedDict()
        attributes = defaultdict(int)
        setters = {
            "Acts.item.topic_id.number": lambda attributes, value: setitem(attributes, "topic_id", value),
            "Acts.item.item_id.number": lambda attributes, value: setitem(attributes, "item_id", value),
            "Acts.item.item_file_id.number": lambda attributes, value: setitem(attributes, "file_id", value),
            "Acts.item.public_title.string": lambda attributes, value: setitem(attributes, "title", value),
            "Acts.item.object_date.string": lambda attributes, value: setitem(attributes, "date", value),
            "Acts.item.end_map": lambda attributes, value: attributes.clear()
        }

        with open(filepath, "r") as f:
            parser = ijson_parse(f)
            for prefix, event, value in parser:
                if (prefix, event) == ("Acts.item", "end_map"):
                    if attributes["topic_id"] in topic_filter and attributes["item_id"] and attributes["file_id"]:
                        files[attributes["item_id"]] = (attributes["file_id"],
                                                        attributes["topic_id"],
                                                        attributes["title"],
                                                        attributes["date"])

                setter = setters.get("".join([prefix, ".", event]))
                if setter:
                    setter(attributes, value)
        return files

    def download_documents(self, topic_filter, id_stop_at=None, delay=None,
                           extract_text=False, callback=None):
        downloaded_files = {}
        documents = self.download_documents_list(topic_filter)
        if len(documents):
            if id_stop_at:
                stop_at = documents.keys().index(id_stop_at)
                documents = OrderedDict(islice(documents.items(), 0, stop_at))

            for item_id, data in documents.items():
                file_id, _, _, _ = data
                url = self.create_document_url(item_id, file_id)
                filename = os_path.join(self.temp_dir, str(item_id))

                downloaded_file = self.download_file(url, filename, extension_from_header=True)
                downloaded_files[item_id] = {"file": downloaded_file, "data": data}

                if extract_text:
                    downloaded_files[item_id]["text"] = self.extract_document_text(downloaded_file)

                if callback:
                    callback(item_id, downloaded_files[item_id])

                if delay:
                    sleep(delay)

        return downloaded_files
