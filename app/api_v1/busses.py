from flask import jsonify, current_app
from . import api
from .. import kovtp
from ..utils import parse_busses_article_or_404, timestamp_to_8601


@api.route("/school-busses/")
def get_busses():
    article_id = current_app.config["JSONWS_BUSSES_ARTICLE_ID"]
    group_id = current_app.config["JSONWS_GROUP_ID"]
    article = kovtp.get_article(group_id, article_id)
    busses = parse_busses_article_or_404(article)
    return jsonify({
        "school_busses": busses,
        "meta": {
            "count": len(busses),
            "next_page": None,
            "previous_page": None}
    })
