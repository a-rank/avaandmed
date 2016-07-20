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

from lxml import etree
from datetime import datetime, timedelta
from re import sub as re_sub


def timestamp_to_8601(timestamp):
    int_timestamp = int(timestamp if timestamp is not None else 0)
    if int_timestamp:
        date = datetime(1970, 1, 1) + timedelta(milliseconds=int_timestamp)
        return date.isoformat()
    else:
        return ""


def get_cdata_from_content(content):
    root = etree.fromstring(content)
    contents = root.xpath("//static-content[@language-id='et_EE']")
    cdata = next(iter(contents), None)
    if cdata is not None:
        return re_sub("[\n\t]", "", cdata.text)
    return None


def get_content_from_article(article):
    if "content" in article:
        return article["content"]
    return None


def kovtp_property(property_name):
    def property_getter(instance):
        return getattr(instance, property_name)

    def property_setter(instance, value):
        if not value:
            raise ValueError
        else:
            setattr(instance, property_name, value)
            
    return property(property_getter, property_setter)
