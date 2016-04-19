import requests, base64, os, shutil, re, math
import fulltext

from pyproj import Proj
from tqdm import tqdm
from xml.etree import ElementTree as et
from pprint import pprint
from sys import exit
from collections import defaultdict, deque