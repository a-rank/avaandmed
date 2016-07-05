from flask import jsonify, current_app, url_for, request
from . import api
from .. import kovtp
from ..utils import Pagination
from ..utils import get_content_or_404, timestamp_to_8601


@api.route("/news/")
def get_all_news():
    page = request.args.get("page", 1, type=int)
    category_id = current_app.config["JSONWS_NEWS_CATEGORY_ID"]
    pagination = Pagination("api.get_all_news", page)
    assets = kovtp.get_asset_entries(category_id, pagination.start(), pagination.end())
    news = []
    for asset in assets:
        asset_id = asset.get("classPK", 0)
        if asset_id:
            news.append({
                "id": asset_id,
                "url": url_for("api.get_news", id=asset_id, _external=True),
                "created_date": timestamp_to_8601(asset.get("createDate", "")),
                "modified_date": timestamp_to_8601(asset.get("modifiedDate", "")),
                "title": asset.get("titleCurrentValue", "")
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
    content = get_content_or_404(article, result_type)
    return jsonify({
        "id": id,
        "created_date": timestamp_to_8601(article.get("createDate", "")),
        "modified_date": timestamp_to_8601(article.get("modifiedDate", "")),
        "title": article.get("titleCurrentValue", ""),
        "url": url_for('api.get_news', id=id, _external=True),
        "links": {
            "images": content["images"],
            "documents": content["documents"],
            "other": content["links"]
        },
        "content": content["text"],
        "portal_url": article.get("urlTitle", "")
    })
