from flask import jsonify
from . import api


@api.route('/news/')
def get_news():
    return jsonify({
        "comments": "empty"
    })
