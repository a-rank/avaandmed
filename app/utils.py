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

from re import sub as re_sub, findall as re_findall
from unicodedata import normalize
from bs4 import BeautifulSoup, NavigableString, Tag
from flask import current_app, url_for


def add_schedule(schedule, element):
    name = normalize("NFKD", unicode(element)).strip()
    if len(name):
        times = re_findall("\d*[,.:]\d{2}", name)
        timetable = []
        for time in times:
            hour, minute = re_sub("[,.]", ":", time).split(":")
            timetable.append("{:02d}:{:s}".format(int(hour), minute))
        schedule.append({"time": timetable, "name": name})


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


def parse_busses_article(cdata):
    result = []
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


def get_article_content_by_type(article, result_type):
    if result_type == "html":
        return article.get_content_as_html()
    else:
        return article.get_content_as_plain_text()


class Pagination(object):
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
