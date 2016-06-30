from flask import jsonify, current_app, url_for
from . import api
from .. import kovtp
from ..utils import extract_content


@api.route("/jobs/")
def get_jobs():
    category_id = current_app.config["JSONWS_JOBS_CATEGORY_ID"]
    assets = kovtp.get_asset_entries(category_id)
    jobs = []
    for asset in assets:
        asset_id = asset["classPK"]
        jobs.append({
            "id": asset_id,
            "url": url_for('api.get_job', id=asset_id, _external=True),
            "created_date": asset["createDate"],
            "expiration_date": asset["expirationDate"],
            "modified_date": asset["modifiedDate"],
            "title": asset["titleCurrentValue"]
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
    content = extract_content(article.get("content", ""))
    return jsonify({
        "id": id,
        "url": url_for('api.get_job', id=id, _external=True),
        "created_date": article["createDate"],
        "expiration_date": article["expirationDate"],
        "title": article["titleCurrentValue"],
        "links": {
            "images": [{"url": image} for image in content["images"]]
        },
        "content": content["text"],
        "portal_url": article["urlTitle"]
    })
