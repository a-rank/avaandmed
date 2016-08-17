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

from uuid import uuid4
import requests
from requests.exceptions import Timeout
from time import sleep
from .exceptions import HttpError
from re import compile


def doku_property():
    property_name = "{}:{}".format("doku", uuid4())

    def property_getter(instance):
        return getattr(instance, property_name)

    def property_setter(instance, value):
        if not value:
            raise ValueError
        else:
            setattr(instance, property_name, value)

    return property(property_getter, property_setter)


def get_with_retries(retries, retry_delay=2, **arguments):
    for i in range(retries):
        try:
            response = requests.get(**arguments)
        except Timeout, ConnectTimeout:
            sleep(retry_delay * i)
            continue
        else:
            return response
    else:
        raise HttpError(requests.codes.timeout, arguments.get("url", ""))


def extract_cadastral(text):
    pattern = compile("\d{5}:\d{3}:\d{4}")
    return set(pattern.findall(text))
