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

from bs4 import BeautifulSoup
from flask import abort
from datetime import datetime, timedelta


def get_content(html):
    result = {"text": "", "images": []}
    soup = BeautifulSoup(html, 'html5lib')
    images = soup.find_all('img', src=True)
    result["images"] = [image["src"] for image in images]
    result["text"] = " ".join(soup.stripped_strings)
    return result


def get_content_or_404(article):
    if not "content" in article:
        abort(404)
    else:
        return get_content(article["content"])


def timestamp_to_8601(timestamp):
    int_timestamp = int(timestamp if timestamp is not None else 0)
    if int_timestamp:
        date = datetime(1970, 1, 1) + timedelta(milliseconds=int_timestamp)
        return date.isoformat()
    else:
        return ""
