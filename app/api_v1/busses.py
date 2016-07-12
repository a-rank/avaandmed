# Copyright 2016 Allan Rank
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        "school_busses": [{"route": r, "schedule": s} for r, s in busses],
        "meta": {
            "count": len(busses),
            "next_page": None,
            "previous_page": None}
    })
