#!/usr/bin/python

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

from flask_script import Manager
from app.context import Doku
from pprint import pprint
from itertools import islice, takewhile
from collections import OrderedDict

manager = Manager(usage="Perform database operations", description="")


def downloaded_callback(files):
    pprint(files)


@manager.command
def fetch():
    "Import documents from amphora"
    app = manager.parent.app
    doku = Doku(amphora_location=app.config["AMPHORA_LOCATION"],
                temp_dir=app.config["TEMP_DIR"])

    documents = doku.download_file_list(app.config["AMPHORA_TOPICS"])
    current_index = documents.keys().index("269660")
    download = dict(islice(documents.items(), 0, current_index))

    downloaded = doku.download_files(file_list=download, delay=0, extract_text=True,
                                     callback=downloaded_callback)

    print len(documents)
