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

import fulltext
import io

from os import path as os_path
from ijson import parse as ijson_parse
from collections import defaultdict, OrderedDict
from operator import setitem
from time import sleep
from cgi import parse_header
from itertools import islice
from re import compile
from pyproj import Proj, transform
from .exceptions import HttpError, ImportError, GeocodeError
from .utils import get_with_retries


class Doku(object):
    geocode_url = "http://geoportaal.maaamet.ee/url/xgis-ky.php"

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

    def extract_document_text(self, filename, encoding="iso-8859-13"):
        _, extension = os_path.splitext(filename)
        type = None
        if not extension in {".doc", ".docx", ".rtf", ".pdf", ".odt"}:
            type = ("application/msword", None)
        text = unicode(fulltext.get(filename, type=type), encoding=encoding)
        return text

    def extract_cadastral(self, text):
        pattern = compile("\d{5}:\d{3}:\d{4}")
        return set(pattern.findall(text))

    def geocode_cadastral(self, cadastral_number, retries=3):
        """Converting cadastral number into geographic coordinates using xgis-ky service
        http://geoportaal.maaamet.ee/est/Teenused/Poordumine-kaardirakendusse-labi-URLi-p9.html#a13

        :param cadastral_number: cadastral number to retrieve coordinates for.
        """
        if not cadastral_number:
            raise ValueError

        result = {"cadastral": cadastral_number}
        querystring = {"what": "tsentroid",
                       "out": "json",
                       "ky": cadastral_number}
        response = get_with_retries(retries, url=self.geocode_url, params=querystring)
        if response.ok:
            try:
                json = response.json()["1"]
                result["x"] = json["X"]
                result["y"] = json["Y"]
            except (ValueError, KeyError):
                raise GeocodeError(cadastral_number)

            wgs84 = Proj(init="epsg:4326")
            lest97 = Proj(init="epsg:3301")
            result["lon"], result["lat"] = transform(lest97, wgs84, json["X"], json["Y"])
            return result
        else:
            raise HttpError(response.status_code, self.geocode_url)

    def download_file(self, url, out_filename, block_size=1024,
                      timeout=20, extension_from_header=False, retries=5):
        response = get_with_retries(retries, url=url, timeout=timeout)
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
            raise HttpError(response.status_code, url)

    def download_documents_list(self, topic_filter):
        filepath = os_path.join(self.temp_dir, "act.json")
        # self.download_file(self.amphora_api_url, filepath)

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

        with io.open(filepath, "r") as f:
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

    def download_documents(self, topic_filter, id_stop_at=None,
                           delay=None, extract_text=False, callback=None):
        downloaded_files = OrderedDict()
        documents = self.download_documents_list(topic_filter)
        if len(documents):
            if id_stop_at:
                stop_at = documents.keys().index(id_stop_at)
                documents = OrderedDict(islice(documents.items(), 0, stop_at))

            for item_id, data in documents.items():
                file_id, _, _, _ = data
                url = self.create_document_url(item_id, file_id)
                filepath = os_path.join(self.temp_dir, str(item_id))
                # downloaded_file = self.download_file(url, filepath, extension_from_header=True)
                ####################
                downloaded_file = filepath
                ####################
                downloaded_files[item_id] = {"file": downloaded_file,
                                             "data": data}
                if extract_text:
                    # text = self.extract_document_text(downloaded_file)
                    text_file = "".join([filepath, ".txt"])
                    ########################
                    text = ""
                    with io.open(text_file, "r") as f:
                        text = f.read()
                    ########################
                    downloaded_files[item_id]["text"] = text_file
                    downloaded_files[item_id]["cadastral"] = self.extract_cadastral(text)
                    with io.open(text_file, "w", encoding="utf8") as f:
                        f.write(text)

                if callback:
                    callback(item_id, downloaded_files[item_id])

                # if delay:
                    # sleep(delay)

        return downloaded_files
