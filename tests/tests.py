#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import base64
import math
import os
import re
import shutil
from collections import defaultdict, deque
from pprint import pprint
from xml.etree import ElementTree as et

import fulltext
import requests
from pyproj import Proj
from tqdm import tqdm


def get_address(member, addresses, proj):
    try:
        for key in member:
            address = member[key]
            coordinates = address["ReferencePoint"]["Point"]["coordinates"].split(",")
            # geo koordinaatide teisaldamine projekteeritud koordinaatidest
            longitude, latitude = proj(coordinates[0], coordinates[1], inverse=True)
            addresses[key].append(
                (address["Tunnus"], address["PikkAadress"], (coordinates[0], coordinates[1]), (latitude, longitude)))
    except KeyError:
        print "parse_address: vigane json"


def get_element_tag(tag):
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def main():
    ###############################################################################
    # minu aadress
    ###############################################################################

    proj = Proj(init="epsg:3301")  # L-EST97 projektsioon

    # VAIKEKOHT,TANAV,KATASTRIYKSUS,EHITISHOONE
    querystring = {
        "dogis_link": "getgazetteer",
        "features": "EHITISHOONE",
        "results": "5"
    }

    address = raw_input("Sisesta otsitav aadress (või vajuta ENTER): ")
    if not address:
        # 25°24'14.586"E 59°29'9.822"N
        # 579555,6595094
        address = "Lõuna tee 15, Mäepea küla"

    # Maa-ameti teenus aadressiinfo (sealhulgas koordinaatide) saamiseks
    # http://geoportaal.maaamet.ee/est/Teenused/X-GIS-JSON-aadressiotsingu-teenuse-kirjeldus-p502.html
    querystring["address"] = address
    response = requests.request('GET', 'http://xgis.maaamet.ee/xGIS/XGis', params=querystring)

    addresses = defaultdict(list)
    try:
        json = response.json()["featureMember"]
        if isinstance(json, dict):
            get_address(json, addresses, proj)
        elif isinstance(json, list):
            for member in json:
                get_address(member, addresses, proj)
    except (ValueError, KeyError):
        print "ei leitud", response.status_code

    response.close()

    tunnus, address, lest97, geo = addresses["EHITISHOONE"][0]
    print "======================================================================="
    print "Leitud aadress:"
    print address
    print "Koordinaadid:"
    pprint(geo)  # geograafilised koordinaadid
    pprint(lest97)  # projekteeritud koordinaadid
    print "======================================================================="

    raw_input("(vajuta ENTER):")

    ###############################################################################
    # amphora teemad
    # Planeerimine ja ehitus - 5059 
    # Detailplaneeringute algatamine - 50285 
    # Detailplaneeringute kehtestamine - 50286 
    # Detailplaneeringute vastuvõtmine - 50287 
    # Projekteerimistingimuste määramine - 50288 
    # Maakorraldus – 50344    
    ###############################################################################

    # kuusalu valla dokumendiregister
    url = "http://server.amphora.ee/atp/kuusaluvv/AmphoraPublic.asmx"
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }

    ###############################################################################

    payload = {
        "type": "DOCUMENT",
        "topicID": "5059",
        "maxRows": "20",
        "unitID": "",
        "folderID": "",
        "formID": "",
        "phrase": "",
        "startRowIndex": "",
        "detailMetadata": ""
    }

    # dokumentide nimekirja päring registrist
    articles = dict()
    response = requests.post(url + "/GetItemList", data=payload, headers=headers, stream=True)
    response.raw.decode_content = True

    # 259449 ja 259430 on suured dokumendid, need jäetakse demo mõttes hetkel välja
    for event, element in et.iterparse(response.raw):
        if get_element_tag(element.tag) == "sys_id" and element.text != "259449" and element.text != "259430":
            articles[element.text] = dict()
        element.clear()

    response.close()

    ###############################################################################
    # dokumendid
    ###############################################################################

    articles_folder = os.path.dirname(os.path.abspath(__file__)) + "/documents/"
    if os.path.exists(articles_folder):
        shutil.rmtree(articles_folder)
    os.makedirs(articles_folder)

    # üksikute dokumentide metadata ja faili päring
    progress = tqdm(articles)
    for key in progress:
        progress.set_description("Dokumendid %s" % key)
        payload = {
            "id": key,
            "maxDepth": "0"
        }

        # dokumendi päring
        response = requests.request("POST", url + "/GetItem", data=payload, headers=headers, stream=True)
        response.raw.decode_content = True

        path = deque()
        content = None
        filename = None
        filetype = None
        for event, element in et.iterparse(response.raw, events=("start", "end")):
            element_tag = get_element_tag(element.tag)
            if event == "start":
                path.append(element_tag)
            elif event == "end":
                if "file" in path:
                    if element_tag == "data":
                        content = base64.decodestring(element.text or "")
                    elif element_tag == "filename":
                        filename = element.text
                    elif element_tag == "type":
                        filetype = element.text
                if element_tag == "field" and "name" in element.attrib and element.attrib["name"] == "Caption":
                    articles[key]["title"] = element.text
                path.pop()
                element.clear()

            if content is not None and filename is not None and filetype == "MAIN_FILE":
                _, extension = os.path.splitext(filename)
                articles[key]["file"] = key + extension
                out = open(articles_folder + key + extension, "wb")  # faili salvestamine
                out.write(content)
                out.close()
                break
        else:
            print "ei sisalda faili", key

        response.close()

    print "======================================================================="

    ###############################################################################
    # failid
    ###############################################################################

    # Maa-ameti teenus koordinaatide pärimiseks katastrinumbri järgi
    # http://geoportaal.maaamet.ee/est/Teenused/Poordumine-kaardirakendusse-labi-URLi-p9.html#a13
    url = "http://geoportaal.maaamet.ee/url/xgis-ky.php"
    querystring = {
        "what": "tsentroid",
        "out": "json"
    }

    # kauguse arvutus projekteeritud koordinaatidega
    point = lambda coordinate: float(coordinate)
    distance = lambda src, dest: math.sqrt(
        (point(src[0]) - point(dest[0])) ** 2 + (point(src[1]) - point(dest[1])) ** 2)

    pattern = re.compile("\d{5}:\d{3}:\d{4}")  # regexp katastrinumbri leindmiseks tekstist
    _, _, x_y, _ = addresses["EHITISHOONE"][0]  # minu aadress
    progress = tqdm(articles)
    for key in progress:
        progress.set_description("Koordinaadid %s" % key)
        articles[key]["katastrinumbrid"] = list()
        if "file" not in articles[key]:
            continue
        text = fulltext.get(articles_folder + articles[key]["file"])  # pdf, doc ja rtf failide konverteerimine tekstiks
        katastrinumbrid = set(pattern.findall(text))
        for number in katastrinumbrid:
            querystring["ky"] = number
            response = requests.request("GET", url, params=querystring)  # koordinaatide päring maaametist
            try:
                json = response.json()["1"]
                distance_km = distance(x_y, (json["X"], json["Y"])) / 1000  # katastrinumbri kaugus minu aadressist
                longitude, latitude = proj(json["X"], json["Y"],
                                           inverse=True)  # katastrinumbri geograafilised koordinaadid (saab otse kopeerida google mapsi)
                articles[key]["katastrinumbrid"].append(
                    (number, (json["X"], json["Y"]), distance_km, (latitude, longitude)))
            except (ValueError, KeyError):
                print "koordinaate ei leitud", response.status_code, key, number
            response.close()

    print "======================================================================="

    for key in articles:
        if articles[key]["katastrinumbrid"]:
            print "---------------"
            print "Dokument:", key, articles[key]["title"]
            print "---------------"
            for number in articles[key]["katastrinumbrid"]:
                knumber, lest97, kaugus, (latitude, longitude) = number
                print knumber, " koordinaadid:", latitude, ",", longitude, " kaugus minu aadressist:", kaugus
            print "======================================================================="


if __name__ == '__main__':
    main()
