from flask import jsonify, current_app, url_for
from . import api
from .. import kovtp
from ..utils import get_content_or_404, timestamp_to_8601


@api.route("/jobs/")
def get_jobs():
    category_id = current_app.config["JSONWS_JOBS_CATEGORY_ID"]
    assets = kovtp.get_asset_entries(category_id)
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
    return jsonify({
        "jobs": jobs,
        "meta": {
            "count": len(assets),
            "next_page": None,
            "previous_page": None}
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
