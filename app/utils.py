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
from flask import current_app, url_for
from lxml import etree
from re import compile as re_compile


def get_content(html, result_type):
    result = {
        "text": "",
        "images": [], "links": [], "documents": []
    }
    root = etree.fromstring(html)
    contents = root.xpath("//static-content[@language-id='et_EE']")
    content = next(iter(contents), None)
    if content is not None:
        soup = BeautifulSoup(content.text, current_app.config["HTML_PARSER"])
        images = soup.find_all("img")
        result["images"] = [{"url": image["src"]} for image in images]

        documents_pattern = re_compile(current_app.config["DOCUMENTS_PATTERN"])
        links = soup.find_all("a")
        for link in links:
            if link["href"].startswith("/documents/"):
                link_url = ''.join([current_app.config["KOVTP_URL"], link["href"]])
            else:
                link_url = link["href"]
            result_link = {"url": link_url, "title": link.get_text(strip=True)}
            if documents_pattern.search(link_url) is not None:
                result["documents"].append(result_link)
            else:
                result["links"].append(result_link)

        if result_type == "html":
            result["text"] = content.text
        else:
            result["text"] = " ".join(soup.stripped_strings)

    return result


def get_content_or_404(article, result_type="plain"):
    if not "content" in article:
        abort(404)
    else:
        return get_content(article["content"], result_type)


def timestamp_to_8601(timestamp):
    int_timestamp = int(timestamp if timestamp is not None else 0)
    if int_timestamp:
        date = datetime(1970, 1, 1) + timedelta(milliseconds=int_timestamp)
        return date.isoformat()
    else:
        return ""


class Pagination:
    def __init__(self, base, page):
        self.base = base
        self.page = page
        self.page_size = current_app.config["PAGE_SIZE"]

    def start(self):
        if self.page >= 1:
            return (self.page - 1) * self.page_size
        else:
            return 0

    def end(self):
        if self.page >= 1:
            return self.page * self.page_size
        else:
            return 0

    def next_url(self, results_count):
        if results_count != self.page_size:
            return None
        else:
            return url_for(self.base, page=self.page + 1, _external=True)

    def prev_url(self):
        if self.page <= 1:
            return None
        else:
            return url_for(self.base, page=self.page - 1, _external=True)
