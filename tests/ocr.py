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

import fulltext
import subprocess
import os


def extract_document_text(filename, encoding="iso-8859-13"):
    name, extension = os.path.splitext(filename)
    type = None
    if not extension in {".doc", ".docx", ".rtf", ".pdf", ".odt"}:
        type = ("application/msword", None)
    text = unicode(fulltext.get(filename, type=type), encoding=encoding)
    if extension == ".pdf" and len(text) == 0:
        process = subprocess.Popen(("pypdfocr", "-l", "est", filename), close_fds=True)
        process.communicate()
        ocr_filename = "{}_ocr{}".format(name, extension)
        if os.path.isfile(ocr_filename):
            os.rename(ocr_filename, filename)
            text = unicode(fulltext.get(filename, type=type), encoding=encoding)
        else:
            print ("failed to ocr: {}".format(filename))
    return text


if __name__ == '__main__':
    text = extract_document_text("/Users/arank/src/avaandmed/temp/12184.pdf")
    print(text)
