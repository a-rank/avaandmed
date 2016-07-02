from flask import jsonify, current_app, url_for, request
from . import api
from .. import kovtp
from ..utils import get_content_or_404, timestamp_to_8601
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
    article = kovtp.get_latest_article(id)
    content = get_content_or_404(article)
    return jsonify({
        "id": id,
        "url": url_for('api.get_job', id=id, _external=True),
        "created_date": timestamp_to_8601(article.get("createDate", "")),
        "expiration_date": timestamp_to_8601(article.get("expirationDate", "")),
        "title": article.get("titleCurrentValue", ""),
        "links": {
            "images": [{"url": image} for image in content["images"]]
        },
        "content": content["text"],
        "portal_url": article.get("urlTitle", "")
    })
