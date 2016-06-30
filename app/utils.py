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


def extract_content(html):
    result = {"text": "", "images": []}
    soup = BeautifulSoup(html, 'html5lib')
    result["text"] = " ".join(soup.stripped_strings)
    links = soup.find_all('img', src=True)
    result["images"] = [link["src"] for link in links]
    return result
