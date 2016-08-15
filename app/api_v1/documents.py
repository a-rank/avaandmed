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

from flask import jsonify, current_app, url_for, request
from . import api
from ..utils import Pagination
from ..models import fetch_documents, fetch_document_or_404


@api.route("/documents/")
def get_documents():
    page = request.args.get("page", 1, type=int)
    pagination = Pagination("api.get_documents", page)
    documents = fetch_documents(pagination.start(), pagination.page_size)
    documents_count = len(documents)
    return jsonify({
        "documents": [document.to_json() for document in documents],
        "meta": {
            "count": documents_count,
            "next_page": pagination.next_url(documents_count),
            "previous_page": pagination.prev_url()}
    })


@api.route("/documents/<int:id>")
def get_document(id):
    document = fetch_document_or_404(id)
    return jsonify(document.to_json())
