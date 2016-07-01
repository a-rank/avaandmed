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

def extract_content(html):
    result = {"text": "", "images": []}
    soup = BeautifulSoup(html, 'html5lib')
    images = soup.find_all('img', src=True)
    result["images"] = [image["src"] for image in images]
    result["text"] = " ".join(soup.stripped_strings)
    return result


def extract_content_or_404(article):
    if not "content" in article:
        abort(404)
    else:
        return extract_content(article["content"])