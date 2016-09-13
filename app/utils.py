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
from flask import current_app, url_for, request


def add_schedule(schedule, element):
    name = normalize("NFKD", unicode(element.string)).strip()
    if len(name):
        times = re_findall("\d*[,.:]\d{2}", name)
        timetable = []
        for time in times:
            hour, minute = re_sub("[,.]", ":", time).split(":")
            if len(hour):
                timetable.append("{:02d}:{:s}".format(int(hour), minute))
        schedule.append({"time": timetable, "name": name})


def parse_busses_article(cdata):
    soup = BeautifulSoup(cdata, current_app.config["HTML_PARSER"])
    tags = soup.find_all("td")

    route = None
    result = []
    for tag in tags:
        if tag.strong is not None:
            route = " ".join(tag.stripped_strings)
            result.append({"route": route, "schedule": []})
        else:
            try:
                add_schedule(result[-1]["schedule"], tag)
            except IndexError:
                pass

    return result


def get_article_content_by_type(article, result_type):
    if result_type == "html":
        return article.get_content_as_html()
    else:
        return article.get_content_as_plain_text()


def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    else:
        return True


def response_headers(response, last_modified=None):
    response.add_etag()
    response.content_length = len(response.get_data())
    if last_modified:
        response.last_modified = last_modified
    return response


class Pagination(object):
    def __init__(self, base, args):
        self.base = base
        self.page_size = current_app.config["PAGE_SIZE"]
        self.page = args.get("page", 1, type=int)
        self.args = args

    def get_params(self, page):
        params = self.args.to_dict()
        params["_external"] = True
        params["page"] = page
        return params

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
            params = self.get_params(self.page + 1)
            return url_for(self.base, **params)

    def prev_url(self):
        if self.page <= 1:
            return None
        else:
            params = self.get_params(self.page - 1)
            return url_for(self.base, **params)
