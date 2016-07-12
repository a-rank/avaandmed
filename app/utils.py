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

from bs4 import BeautifulSoup, NavigableString, Tag
from flask import abort
from datetime import datetime, timedelta
from flask import current_app, url_for
from lxml import etree
from re import compile as re_compile, sub as re_sub, findall as re_findall
from unicodedata import normalize


def get_cdata_from_content_or_404(content):
    root = etree.fromstring(content)
    contents = root.xpath("//static-content[@language-id='et_EE']")
    cdata = next(iter(contents), None)
    if cdata is None:
        abort(404)
    return re_sub("[\n\t]", "", cdata.text)


def get_content_from_article_or_404(article):
    if not "content" in article:
        abort(404)
    return article["content"]


def parse_article_or_404(article, result_type="plain"):
    text = None
    images = []
    links = []
    documents = []

    content = get_content_from_article_or_404(article)
    cdata = get_cdata_from_content_or_404(content)
    soup = BeautifulSoup(cdata, current_app.config["HTML_PARSER"])

    image_tags = soup.find_all("img")
    images = [{"url": tag["src"]} for tag in image_tags]

    documents_pattern = re_compile(current_app.config["DOCUMENTS_PATTERN"])
    link_tags = soup.find_all("a")
    for tag in link_tags:
        if tag["href"].startswith("/documents/"):
            link_url = ''.join([current_app.config["KOVTP_URL"], tag["href"]])
        else:
            link_url = tag["href"]

        result_link = {"url": link_url, "title": tag.get_text(strip=True)}
        if documents_pattern.search(link_url) is not None:
            documents.append(result_link)
        else:
            links.append(result_link)

    if result_type == "html":
        text = cdata
    else:
        text = " ".join(soup.stripped_strings)

    return (text, images, links, documents)


def add_schedule(schedule, element):
    text = normalize("NFKD", unicode(element)).strip()
    if len(text):
        timetable = re_findall("\d{1},\d{2}", text)
        schedule.append([timetable, text])


def traverse_schedule_tree(schedule, route, element):
    for child in element.children:
        if isinstance(child, Tag):
            route = traverse_schedule_tree(schedule, route, child)
        elif isinstance(child, NavigableString):
            if route is None:
                route = unicode(child).strip()
            else:
                add_schedule(schedule, child)
    return route


def parse_busses_article_or_404(article):
    result = []
    content = get_content_from_article_or_404(article)
    cdata = get_cdata_from_content_or_404(content)
    soup = BeautifulSoup(cdata, current_app.config["HTML_PARSER"])

    paragraph_tags = soup.find_all("p")
    route = None
    for tag in paragraph_tags:
        schedule = []
        route = traverse_schedule_tree(schedule, route, tag)

        if len(schedule):
            result.append((route, schedule))
            route = None
        if tag.strong is None:
            route = None

    return result


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
