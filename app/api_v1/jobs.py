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
from ..utils import parse_article_or_404, timestamp_to_8601
from ..utils import Pagination


@api.route("/jobs/")
def get_jobs():
    page = request.args.get('page', 1, type=int)
    category_id = current_app.config["JSONWS_JOBS_CATEGORY_ID"]
    pagination = Pagination("api.get_jobs", page)
    assets = kovtp.get_asset_entries(category_id, pagination.start(), pagination.end())
    jobs = []
    for asset in assets:
        asset_id = asset.get("classPK", 0)
        if asset_id:
            jobs.append({
                "id": asset_id,
                "url": url_for('api.get_job', id=asset_id, _external=True),
                "created_date": timestamp_to_8601(asset.get("createDate", "")),
                "expiration_date": timestamp_to_8601(asset.get("expirationDate", "")),
                "modified_date": timestamp_to_8601(asset.get("modifiedDate", "")),
                "title": asset.get("titleCurrentValue", "")
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
def get_job(id):
    result_type = request.args.get("result", "plain", type=str)
    article = kovtp.get_latest_article(id)
    text, images, links, documents = parse_article_or_404(article, result_type)
    return jsonify({
        "id": id,
        "url": url_for('api.get_job', id=id, _external=True),
        "created_date": timestamp_to_8601(article.get("createDate", "")),
        "expiration_date": timestamp_to_8601(article.get("expirationDate", "")),
        "title": article.get("titleCurrentValue", ""),
        "links": {
            "images": images,
            "documents": documents,
            "other": links
        },
        "content": text,
        "portal_url": article.get("urlTitle", "")
    })
