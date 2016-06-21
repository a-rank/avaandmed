from flask import jsonify
from . import api

@api.route('/toopakkumised/')
def get_toopakkumised():
    return jsonify({
        "comments": "empty"
    })