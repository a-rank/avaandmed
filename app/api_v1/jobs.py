from flask import jsonify
from . import api


@api.route('/jobs/')
def get_jobs():
    return jsonify({
        "comments": "empty"
    })
