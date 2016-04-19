#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests, base64, os, shutil, re, math
import fulltext

from pyproj import Proj
from tqdm import tqdm
from xml.etree import ElementTree as et
from pprint import pprint
from sys import exit
from collections import defaultdict, deque

def get_address(member, addresses, proj):
    try:
        for key in member:
            address = member[key]
            coordinates = address["ReferencePoint"]["Point"]["coordinates"].split(",")
            longitude, latitude = proj(coordinates[0], coordinates[1], inverse=True)
            addresses[key].append((address["Tunnus"], address["PikkAadress"], (coordinates[0], coordinates[1]), (latitude, longitude)))    
    except KeyError:
        print "parse_address: key not found"

def get_element_tag(tag):
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag    

def main():

    ###############################################################################
    # my address
    ###############################################################################

    # VAIKEKOHT,TANAV,KATASTRIYKSUS,EHITISHOONE
    querystring = {
        "dogis_link" : "getgazetteer",
        "features" : "EHITISHOONE", 
        "results" : "5"
        }

    #25°24'14.586"E 59°29'9.822"N
    #579555,6595094

    address = raw_input('Sisesta otsitav aadress: ')
    if not address:
        address = "Lõuna tee 15, Mäepea küla"

    querystring["address"] = address
    response = requests.request("GET", "http://xgis.maaamet.ee/xGIS/XGis", params = querystring)
    proj = Proj(init="epsg:3301") #L-EST97

    addresses = defaultdict(list)
    try:
        json = response.json()["featureMember"]
        if isinstance(json, dict):
            get_address(json, addresses, proj)
        elif isinstance(json, list):
            for member in json:
                get_address(member, addresses, proj)
    except (ValueError, KeyError):
        print "address not found", response.status_code

    response.close()

    tunnus, address, lest97, wgs94 = addresses["EHITISHOONE"][0]
    print "======================================================================="
    print "Leitud aadress:"
    print address
    print "Koordinaadid:"
    pprint(wgs94)
    pprint(lest97)
    print "======================================================================="

    raw_input()

    ###############################################################################
    # amphora articles
    # Planeerimine ja ehitus - 5059 
    # Detailplaneeringute algatamine - 50285 
    # Detailplaneeringute kehtestamine - 50286 
    # Detailplaneeringute vastuvõtmine - 50287 
    # Projekteerimistingimuste määramine - 50288 
    # Maakorraldus – 50344    
    ###############################################################################

    url = "http://server.amphora.ee/atp/kuusaluvv/AmphoraPublic.asmx"
    headers = {
        "content-type": "application/x-www-form-urlencoded"
        }

    ###############################################################################

    payload = {
    	"type" : "DOCUMENT", 
        "topicID" : "5059", 
        "maxRows" : "20",
    	"unitID" : "", 
        "folderID" : "", 
        "formID" : "", 
        "phrase" : "", 
        "startRowIndex" : "", 
        "detailMetadata" : ""
    	}    	

    articles = dict()
    response = requests.post(url + "/GetItemList", data = payload, headers = headers, stream = True)
    response.raw.decode_content = True
    
    for event, element in et.iterparse(response.raw):
        if get_element_tag(element.tag) == "sys_id" and element.text != "259449" and element.text != "259430":
            articles[element.text] = dict()
        element.clear()

    response.close()
    ###############################################################################
    # articles
    ###############################################################################

    articles_folder = "/Users/arank/src/maa/tmp/"
    if os.path.exists(articles_folder):
        shutil.rmtree(articles_folder) 
    os.makedirs(articles_folder)

    progress = tqdm(articles)
    for key in progress:
        progress.set_description("Dokumendid %s" % key)
        payload = {
            "id" : key, 
            "maxDepth" : "0"
        }
        response = requests.request("POST", url + "/GetItem", data=payload, headers=headers, stream = True)
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
                out = open(articles_folder + key + extension, "wb")
                out.write(content)
                out.close()
                break
        else:
            print "no data for ", key 

        response.close()

    print "======================================================================="

    ###############################################################################
    # files
    ###############################################################################

    url = "http://geoportaal.maaamet.ee/url/xgis-ky.php"
    querystring = {
        "what":"tsentroid",
        "out":"json"
    }
    
    pattern = re.compile("\d{5}:\d{3}:\d{4}")
    _, _, (x, y), wgs94 = addresses["EHITISHOONE"][0]
    progress = tqdm(articles)
    for key in progress:
        progress.set_description("Koordinaadid %s" % key)
        articles[key]["katastrinumbrid"] = list()
        text = fulltext.get(articles_folder + articles[key]["file"])
        katastrinumbrid = set(pattern.findall(text))
        for number in katastrinumbrid:
            querystring["ky"] = number
            response = requests.request("GET", url, params=querystring)
            try:
                json = response.json()["1"]
                distance_km = math.sqrt((float(json["X"]) - float(x)) ** 2 + (float(json["Y"]) - float(y)) ** 2) / 1000
                longitude, latitude = proj(json["X"], json["Y"], inverse=True) #long / lat
                articles[key]["katastrinumbrid"].append((number, (json["X"], json["Y"]), distance_km, (latitude, longitude))) 
            except (ValueError, KeyError):
                print "coordinates not found", response.status_code
            response.close()                

    print "======================================================================="

    for key in progress:
        if articles[key]["katastrinumbrid"]:
            print "---------------"
            print "Dokument: ", key, articles[key]["title"]
            print "---------------"
            for number in articles[key]["katastrinumbrid"]:
                knumber, lest97, kaugus, (latitude, longitude) = number
                print knumber, " koordinaadid:", latitude, ",", longitude, " kaugus leitud aadressist:", format(kaugus, '.2f')
            print "======================================================================="

if __name__ == '__main__':
    main()








