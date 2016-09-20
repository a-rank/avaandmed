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
import utils
import subprocess
import os

from ijson import parse as ijson_parse
from collections import defaultdict, OrderedDict
from operator import setitem
from time import sleep
from cgi import parse_header
from itertools import islice
from pyproj import Proj, transform
from .exceptions import HttpError, GeocodeError
from uuid import uuid1


class Doku(object):
    geocode_url = "http://geoportaal.maaamet.ee/url/xgis-ky.php"

    def __init__(self, amphora_location):
        if not amphora_location:
            raise ValueError
        else:
            self.amphora_url = "http://atp.amphora.ee/{location}".format(location=amphora_location)
            self.amphora_api_url = "{amphora_url}/api/item".format(amphora_url=self.amphora_url)

    def create_document_url(self, item_id, item_file_id):
        return "{amphora_url}/?itm={itm}&af={af}".format(amphora_url=self.amphora_url,
                                                         itm=item_id, af=item_file_id)

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
        response = utils.get_with_retries(retries, url=self.geocode_url, params=querystring)
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
        response = utils.get_with_retries(retries, url=url, timeout=timeout)
        if response.ok:
            if extension_from_header:
                _, params = parse_header(response.headers.get("content-disposition", ""))
                _, extension = os.path.splitext(params.get("filename", ""))
                if extension:
                    out_filename = "".join([out_filename, extension])
            with open(out_filename, "w") as f:
                for block in response.iter_content(block_size):
                    f.write(block)
            return out_filename
        else:
            raise HttpError(response.status_code, url)

    def extract_document_text(self, filename, encoding="iso-8859-13", language="est"):
        name, extension = os.path.splitext(filename)
        type = None
        if not extension in {".doc", ".docx", ".rtf", ".pdf", ".odt"}:
            type = ("application/msword", None)
        text = unicode(fulltext.get(filename, type=type), encoding=encoding)
        if extension == ".pdf" and len(text) == 0:
            process = subprocess.Popen(("pypdfocr", "-l", language, filename), close_fds=True)
            process.communicate()
            ocr_filename = "{}_ocr{}".format(name, extension)
            if os.path.isfile(ocr_filename):
                os.rename(ocr_filename, filename)
                text = unicode(fulltext.get(filename, type=type), encoding=encoding)
            else:
                print ("failed to ocr: {}".format(filename))
        return text

    def download_documents_list(self, topic_filter, folder):
        filepath = os.path.join(folder, "".join([uuid1().hex, ".json"]))
        self.download_file(self.amphora_api_url, filepath)

        files = OrderedDict()
        attributes = defaultdict(int)
        setters = {
            "Items.item.topic_id.number": lambda attributes, value: setitem(attributes, "topic_id", value),
            "Items.item.item_id.number": lambda attributes, value: setitem(attributes, "item_id", value),
            "Items.item.item_file_id.number": lambda attributes, value: setitem(attributes, "file_id", value),
            "Items.item.public_title.string": lambda attributes, value: setitem(attributes, "title", value),
            "Items.item.object_date.string": lambda attributes, value: setitem(attributes, "date", value),
            "Items.item.end_map": lambda attributes, value: attributes.clear()
        }

        with io.open(filepath, "r") as f:
            parser = ijson_parse(f)
            for prefix, event, value in parser:
                if (prefix, event) == ("Items.item", "end_map"):
                    if attributes["topic_id"] in topic_filter and attributes["item_id"] and attributes["file_id"]:
                        files[attributes["item_id"]] = (attributes["file_id"],
                                                        attributes["topic_id"],
                                                        attributes["title"],
                                                        attributes["date"])

                setter = setters.get("".join([prefix, ".", event]))
                if setter:
                    setter(attributes, value)
        return files

    def download_documents(self, topic_filter, folder, id_stop_at=None, delay=None,
                           extract_text=False, callback=None, overwrite=False):
        downloaded_files = OrderedDict()
        documents = self.download_documents_list(topic_filter, folder)
        if len(documents):
            if id_stop_at:
                stop_at = documents.keys().index(id_stop_at)
                documents = OrderedDict(islice(documents.items(), 0, stop_at))

            existing_files = []
            if not overwrite:
                existing_files = os.listdir(folder)

            for item_id, data in documents.items():
                file_id, _, _, _ = data
                filepath = os.path.join(folder, str(item_id))

                existing_file = utils.filter_files_exclude(existing_files,
                                                           "".join([str(item_id), ".*"]), "*.txt")
                if not overwrite and existing_file is not None:
                    downloaded_file = os.path.join(folder, existing_file)
                    print ("found existing document: {}".format(existing_file))
                else:
                    url = self.create_document_url(item_id, file_id)
                    downloaded_file = self.download_file(url, filepath, extension_from_header=True)
                    if delay:
                        sleep(delay)

                downloaded_files[item_id] = {"file": downloaded_file,
                                             "data": data}

                if extract_text:
                    text_file = "".join([filepath, ".txt"])
                    if not overwrite and os.path.isfile(text_file):
                        with io.open(text_file, "r", encoding="utf8") as f:
                            text = f.read()
                        print ("found existing text file: {}".format(text_file))
                    else:
                        text = self.extract_document_text(downloaded_file)
                        with io.open(text_file, "w", encoding="utf8") as f:
                            f.write(text)
                    downloaded_files[item_id]["text"] = text_file
                    downloaded_files[item_id]["cadastral"] = utils.extract_cadastral(text)

                if callback:
                    callback(item_id, downloaded_files[item_id])

        return downloaded_files
