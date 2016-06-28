from flask import jsonify
from . import api
from .. import kovtp


@api.route('/jobs/')
def get_jobs():
    return jsonify({
        "jsonws_url": kovtp.jsonws_url
    })
