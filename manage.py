#!/usr/bin/python

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

from app import create_app
from flask_script import Manager, Server
from config import DevConfig, ProdConfig

app = create_app(DevConfig)
manager = Manager(app=app, with_default_commands=False)
manager.add_command("server", Server())


@manager.shell
def make_shell_context():
    return dict(
        app=app
    )


@manager.command
def fetch():
    "Import documents from amphora"
    pass


if __name__ == '__main__':
    manager.run()
