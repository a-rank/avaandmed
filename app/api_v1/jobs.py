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
from .. import cache, kovtp
from ..utils import Pagination, get_article_content_by_type, cache_key


@api.route("/jobs/")
@cache.cached(key_prefix=cache_key)
def get_jobs():
    category_id = current_app.config["JSONWS_JOBS_CATEGORY_ID"]
    pagination = Pagination("api.get_jobs", request.args)
    assets = kovtp.get_assets(category_id, pagination.start(), pagination.end())
    jobs = []
    for asset in assets:
        article_primary_key = asset.get_primary_key()
        if article_primary_key:
            jobs.append({
                "id": article_primary_key,
                "url": url_for("api.get_job", id=article_primary_key, _external=True),
                "created_date": asset.get_create_date(),
                "expiration_date": asset.get_expiration_date(),
                "modified_date": asset.get_modified_date(),
                "title": asset.get_title()
            })
    assets_count = len(assets)
    return jsonify({
        "jobs": jobs,
        "meta": {
            "count": assets_count,
            "next_page": pagination.next_url(assets_count),
            "previous_page": pagination.prev_url()}
    })


@api.route("/jobs/<int:id>")
@cache.cached(key_prefix=cache_key)
def get_job(id):
    result_type = request.args.get("result", "plain", type=str)
    article = kovtp.get_latest_article(id)
    links, documents = article.get_document_links()
    return jsonify({
        "id": id,
        "url": url_for("api.get_job", id=id, _external=True),
        "created_date": article.get_create_date(),
        "expiration_date": article.get_expiration_date(),
        "title": article.get_title(),
        "links": {
            "images": article.get_image_links(),
            "documents": documents,
            "other": links
        },
        "content": get_article_content_by_type(article, result_type),
        "portal_url": article.get_url_title()
    })
