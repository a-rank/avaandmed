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

from urlparse import urlparse
from utils import get_content_from_article, get_cdata_from_content
from bs4 import BeautifulSoup
from re import compile
from .utils import timestamp_to_8601


class Article:
    document_extensions = "(\.pdf)|(\.doc)|(\.docx)|(\.bdoc)|(\.odt)|(\.xls)|(\.ods)|(\.dwg)|(\.rtf)"

    def __init__(self, article, base_url, html_parser, document_extensions=None):
        if not isinstance(article, dict):
            raise TypeError
        self.article = article

        self.content = get_content_from_article(article)
        if self.content is None:
            raise ValueError
        self.cdata = get_cdata_from_content(self.content)
        if self.cdata is None:
            raise ValueError

        self.soup = BeautifulSoup(self.cdata, html_parser)
        self.base_url = base_url
        if document_extensions is not None:
            self.document_extensions = document_extensions

    def __repr__(self):
        return '<Article {}>'.format(self.get_article_id())

    def get_article_id(self):
        return self.article.get("articleId", 0)

    def get_company_id(self):
        return self.article.get("companyId", 0)

    def get_create_date(self):
        return timestamp_to_8601(self.article.get("createDate", ""))

    def get_expiration_date(self):
        return timestamp_to_8601(self.article.get("expirationDate", ""))

    def get_modified_date(self):
        return timestamp_to_8601(self.article.get("modifiedDate", ""))

    def get_description(self):
        return self.article.get("description", "")

    def get_group_id(self):
        return self.article.get("groupId", 0)

    def get_primary_key(self):
        return self.article.get("resourcePrimKey", "")

    def get_title(self):
        return self.article.get("titleCurrentValue", "")

    def get_url_title(self):
        return self.article.get("urlTitle", "")

    def get_uuid(self):
        return self.article.get("uuid", "")

    def get_version(self):
        return self.article.get("version", "")

    def get_raw(self):
        return self.article

    def get_content_as_html(self):
        return self.cdata

    def get_content_as_plain_text(self):
        return " ".join(self.soup.stripped_strings)

    def get_image_links(self):
        image_tags = self.soup.find_all("img")
        return [{"url": tag["src"]} for tag in image_tags]

    def get_document_links(self):
        links = []
        documents = []

        pattern = compile(self.document_extensions)
        link_tags = self.soup.find_all("a")
        for tag in link_tags:
            try:
                result = urlparse(tag["href"])
                if not result.scheme:
                    url = "".join([self.base_url, result.geturl()])
                else:
                    url = result.geturl()
            except AttributeError:
                continue

            result = {"url": url, "title": tag.get_text(strip=True)}
            if pattern.search(url) is not None:
                documents.append(result)
            else:
                links.append(result)

        return (links, documents)
