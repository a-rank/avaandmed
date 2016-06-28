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

from flask import Flask
from .context import Kovtp

kovtp = Kovtp()

def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config)
    app.url_map.strict_slashes = False

    kovtp.jsonws_url = app.config["JSONWS_URL"]
    kovtp.jsonws_username = app.config["JSONWS_USERNAME"]
    kovtp.jsonws_password = app.config["JSONWS_PASSWORD"]

    from api_v1 import api as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix='/v1')

    return app
