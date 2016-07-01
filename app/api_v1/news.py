from flask import jsonify, current_app, url_for, abort
from . import api
from .. import kovtp
from ..utils import extract_content_or_404


@api.route("/news/")
def get_all_news():
    category_id = current_app.config["JSONWS_NEWS_CATEGORY_ID"]
    assets = kovtp.get_asset_entries(category_id)
    news = []
    for asset in assets:
        asset_id = asset["classPK"]
        news.append({
            "id": asset_id,
            "url": url_for('api.get_news', id=asset_id, _external=True),
            "created_date": asset["createDate"],
            "modified_date": asset["modifiedDate"],
            "title": asset["titleCurrentValue"]
        })
    return jsonify({
        "news": news,
        "meta": {
            "count": len(assets),
            "next_page": None,
            "previous_page": None}
    })


@api.route("/news/<int:id>")
def get_news(id):
    article = kovtp.get_latest_article(id)
    content = extract_content_or_404(article)
    return jsonify({
        "id": id,
        "created_date": article["createDate"],
        "modified_date": article["modifiedDate"],
        "title": article["titleCurrentValue"],
        "url": url_for('api.get_news', id=id, _external=True),
        "links": {
            "images": [{"url": image} for image in content["images"]]
        },
        "content": content["text"],
        "portal_url": article["urlTitle"]
    })
