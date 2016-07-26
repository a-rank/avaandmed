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
