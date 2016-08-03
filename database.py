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

manager = Manager(usage="Perform database operations", description="")


def downloaded_callback(id, files):
    print id


@manager.command
def fetch():
    "Import documents from amphora"
    app = manager.parent.app
    doku = Doku(amphora_location=app.config["AMPHORA_LOCATION"],
                temp_dir=app.config["TEMP_DIR"])

    # 269660
    downloaded = doku.download_documents(id_stop_at=269660, topic_filter=app.config["AMPHORA_TOPICS"],
                                         delay=5, extract_text=True, callback=downloaded_callback)
    print len(downloaded)
