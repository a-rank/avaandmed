from flask import jsonify, current_app, url_for
from . import api
from .. import kovtp
from datetime import datetime

@api.route("/jobs/")
def get_jobs():
    category_id = current_app.config["JOBS_CATEGORY_ID"]
    assets = kovtp.get_asset_entries(category_id)
    jobs = []
    for asset in assets:
        asset_id = asset["classPK"]
        jobs.append({
            "id": asset_id,
            "url": url_for('api.get_job', id=asset_id, _external=True),
            "created_date": asset["createDate"],
            "expiration_date": asset["expirationDate"],
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
    return jsonify({
        "jsonws_url": kovtp.jsonws_url
    })
