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

import mysql.connector

from flask import current_app
from flask import _app_ctx_stack as stack


class MySQLConnector(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("MYSQL_HOST", "localhost")
        app.config.setdefault("MYSQL_USER", None)
        app.config.setdefault("MYSQL_PASSWORD", None)
        app.config.setdefault("MYSQL_DB", None)
        app.config.setdefault("MYSQL_PORT", 3306)
        app.config.setdefault("MYSQL_UNIX_SOCKET", None)
        app.config.setdefault("MYSQL_USE_UNICODE", True)
        app.config.setdefault("MYSQL_CHARSET", "utf8")
        app.config.setdefault("MYSQL_AUTOCOMMIT", False)
        app.config.setdefault("MYSQL_TIME_ZONE", None)
        app.config.setdefault("MYSQL_SQL_MODE", None)
        app.config.setdefault("MYSQL_CONNECTION_TIMEOUT", 10)
        app.config.setdefault("MYSQL_CLIENT_FLAGS", None)
        app.config.setdefault("MYSQL_BUFFERED", False)
        app.config.setdefault("MYSQL_RAW", False)
        app.config.setdefault("MYSQL_CONSUME_RESULTS", False)
        app.config.setdefault("MYSQL_AUTH_PLUGIN", None)
        app.config.setdefault("MYSQL_COLLATION", "utf8_general_ci")
        app.config.setdefault("MYSQL_GET_WARNINGS", False)
        app.config.setdefault("MYSQL_RAISE_ON_WARNINGS", False)
        app.config.setdefault("MYSQL_SSL_CA", None)
        app.config.setdefault("MYSQL_SSL_CERT", None)
        app.config.setdefault("MYSQL_SSL_KEY", None)
        app.config.setdefault("MYSQL_SSL_VERIFY_CERT", False)
        app.config.setdefault("MYSQL_FORCE_IPV6", False)
        app.config.setdefault("MYSQL_POOL_NAME", None)
        app.config.setdefault("MYSQL_POOL_SIZE", 5)
        app.config.setdefault("MYSQL_POOL_RESET_SESSION", True)
        app.config.setdefault("MYSQL_COMPRESS", False)
        app.config.setdefault("MYSQL_CONVERTER_CLASS", None)
        app.config.setdefault("MYSQL_FABRIC", None)
        app.config.setdefault("MYSQL_FAILOVER", None)
        app.config.setdefault("MYSQL_OPTION_FILES", None)
        app.config.setdefault("MYSQL_OPTION_GROUPS", None)
        app.config.setdefault("MYSQL_ALLOW_LOCAL_INFILE", True)
        app.config.setdefault("MYSQL_USE_PURE", False)

        if hasattr(app, "teardown_appcontext"):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def connect(self):
        arguments = {}
        if current_app.config["MYSQL_HOST"]:
            arguments["host"] = current_app.config["MYSQL_HOST"]

        if current_app.config["MYSQL_USER"]:
            arguments["user"] = current_app.config["MYSQL_USER"]

        if current_app.config["MYSQL_PASSWORD"]:
            arguments["password"] = current_app.config["MYSQL_PASSWORD"]

        if current_app.config["MYSQL_DB"]:
            arguments["database"] = current_app.config["MYSQL_DB"]

        if current_app.config["MYSQL_PORT"]:
            arguments["port"] = current_app.config["MYSQL_PORT"]

        if current_app.config["MYSQL_UNIX_SOCKET"]:
            arguments["unix_socket"] = current_app.config["MYSQL_UNIX_SOCKET"]

        if current_app.config["MYSQL_USE_UNICODE"]:
            arguments["use_unicode"] = current_app.config["MYSQL_USE_UNICODE"]

        if current_app.config["MYSQL_CHARSET"]:
            arguments["charset"] = current_app.config["MYSQL_CHARSET"]

        if current_app.config["MYSQL_AUTOCOMMIT"]:
            arguments["autocommit"] = current_app.config["MYSQL_AUTOCOMMIT"]

        if current_app.config["MYSQL_TIME_ZONE"]:
            arguments["time_zone"] = current_app.config["MYSQL_TIME_ZONE"]

        if current_app.config["MYSQL_SQL_MODE"]:
            arguments["sql_mode"] = current_app.config["MYSQL_SQL_MODE"]

        if current_app.config["MYSQL_CONNECTION_TIMEOUT"]:
            arguments["connection_timeout"] = current_app.config["MYSQL_CONNECTION_TIMEOUT"]

        if current_app.config["MYSQL_CLIENT_FLAGS"]:
            arguments["client_flags"] = current_app.config["MYSQL_CLIENT_FLAGS"]

        if current_app.config["MYSQL_BUFFERED"]:
            arguments["buffered"] = current_app.config["MYSQL_BUFFERED"]

        if current_app.config["MYSQL_RAW"]:
            arguments["raw"] = current_app.config["MYSQL_RAW"]

        if current_app.config["MYSQL_CONSUME_RESULTS"]:
            arguments["consume_results"] = current_app.config["MYSQL_CONSUME_RESULTS"]

        if current_app.config["MYSQL_AUTH_PLUGIN"]:
            arguments["auth_plugin"] = current_app.config["MYSQL_AUTH_PLUGIN"]

        if current_app.config["MYSQL_COLLATION"]:
            arguments["collation"] = current_app.config["MYSQL_COLLATION"]

        if current_app.config["MYSQL_GET_WARNINGS"]:
            arguments["get_warnings"] = current_app.config["MYSQL_GET_WARNINGS"]

        if current_app.config["MYSQL_RAISE_ON_WARNINGS"]:
            arguments["raise_on_warnings"] = current_app.config["MYSQL_RAISE_ON_WARNINGS"]

        if current_app.config["MYSQL_SSL_CA"]:
            arguments["ssl_ca"] = current_app.config["MYSQL_SSL_CA"]

        if current_app.config["MYSQL_SSL_CERT"]:
            arguments["ssl_cert"] = current_app.config["MYSQL_SSL_CERT"]

        if current_app.config["MYSQL_SSL_KEY"]:
            arguments["ssl_key"] = current_app.config["MYSQL_SSL_KEY"]

        if current_app.config["MYSQL_SSL_VERIFY_CERT"]:
            arguments["ssl_verify_cert"] = current_app.config["MYSQL_SSL_VERIFY_CERT"]

        if current_app.config["MYSQL_FORCE_IPV6"]:
            arguments["force_ipv6"] = current_app.config["MYSQL_FORCE_IPV6"]

        if current_app.config["MYSQL_POOL_NAME"]:
            arguments["pool_name"] = current_app.config["MYSQL_POOL_NAME"]

        if current_app.config["MYSQL_POOL_SIZE"]:
            arguments["pool_size"] = current_app.config["MYSQL_POOL_SIZE"]

        if current_app.config["MYSQL_POOL_RESET_SESSION"]:
            arguments["pool_reset_session"] = current_app.config["MYSQL_POOL_RESET_SESSION"]

        if current_app.config["MYSQL_COMPRESS"]:
            arguments["compress"] = current_app.config["MYSQL_COMPRESS"]

        if current_app.config["MYSQL_CONVERTER_CLASS"]:
            arguments["converter_class"] = current_app.config["MYSQL_CONVERTER_CLASS"]

        if current_app.config["MYSQL_FABRIC"]:
            arguments["fabric"] = current_app.config["MYSQL_FABRIC"]

        if current_app.config["MYSQL_FAILOVER"]:
            arguments["failover"] = current_app.config["MYSQL_FAILOVER"]

        if current_app.config["MYSQL_OPTION_FILES"]:
            arguments["option_files"] = current_app.config["MYSQL_OPTION_FILES"]

        if current_app.config["MYSQL_OPTION_GROUPS"]:
            arguments["option_groups"] = current_app.config["MYSQL_OPTION_GROUPS"]

        if current_app.config["MYSQL_ALLOW_LOCAL_INFILE"]:
            arguments["allow_local_infile"] = current_app.config["MYSQL_ALLOW_LOCAL_INFILE"]

        if current_app.config["MYSQL_USE_PURE"]:
            arguments["USE_PURE"] = current_app.config["MYSQL_USE_PURE"]

        return mysql.connector.connect(**arguments)

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, "mysql_connector"):
            ctx.mysql_connector.close()

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, "mysql_connector"):
                ctx.mysql_connector = self.connect()
            return ctx.mysql_connector
