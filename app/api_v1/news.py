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

from flask import jsonify, current_app, url_for, request
from . import api
from .. import kovtp
from ..utils import Pagination, get_article_content_by_type


@api.route("/news/")
def get_all_news():
    category_id = current_app.config["JSONWS_NEWS_CATEGORY_ID"]
    pagination = Pagination("api.get_all_news", request.args)
    assets = kovtp.get_assets(category_id, pagination.start(), pagination.end())
    news = []
    for asset in assets:
        article_primary_key = asset.get_primary_key()
        if article_primary_key:
            news.append({
                "id": article_primary_key,
                "url": url_for("api.get_news", id=article_primary_key, _external=True),
                "created_date": asset.get_create_date(),
                "modified_date": asset.get_modified_date(),
                "title": asset.get_title()
            })
    assets_count = len(assets)
    return jsonify({
        "news": news,
        "meta": {
            "count": assets_count,
            "next_page": pagination.next_url(assets_count),
            "previous_page": pagination.prev_url()}
    })


@api.route("/news/<int:id>")
def get_news(id):
    result_type = request.args.get("result", "plain", type=str)
    article = kovtp.get_latest_article(id)
    links, documents = article.get_document_links()
    return jsonify({
        "id": id,
        "created_date": article.get_create_date(),
        "modified_date": article.get_modified_date(),
        "title": article.get_title(),
        "url": url_for("api.get_news", id=id, _external=True),
        "links": {
            "images": article.get_image_links(),
            "documents": documents,
            "other": links
        },
        "content": get_article_content_by_type(article, result_type),
        "portal_url": article.get_url_title()
    })
