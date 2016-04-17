# -*- coding: utf-8 -*-
"""
See readme.md

"""

from lxml.html import document_fromstring
import simplekml

from urllib.request import FancyURLopener

import os
import re
import sys
import time

coords_in_content = re.compile('\/@(-?\d+\.\d+),(-?\d+\.\d+),')
mobile_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'

filename = r'GoogleBookmarks.html'
if(len(sys.argv) > 1):
    filename = sys.argv[1]

print('opening ' + filename)
with open(filename) as bookmarks_file:
    data = bookmarks_file.read()

doc = document_fromstring(data)

class Browser(FancyURLopener):
    version = mobile_agent

for label in doc.body.iterfind('dl/dt/h3'):
    labelName = label.text_content()

    kml = simplekml.Kml()
    kml.document.name = labelName

    for element, attribute, url, pos in label.getparent().getnext().iterlinks():
        if 'maps.google' in url:
            print
            description = element.text or ''
            print('GET {0} {1}'.format(url, description.encode('UTF8')))
            browser = Browser()

            # Load map and find coordinates in source of page
            sock = False
            while not sock:
                try:
                    sock = browser.open(url.replace(' ','+'))
                except Exception as e:
                    print('Connection problem:' + repr(e))
                    print('Retrying randomly between 15 and 60 seconds.')
                    time.sleep(random.randint(15, 60))

            content = sock.read().decode("utf-8")
            sock.close()

            try:
                coords = coords_in_content.search(content).groups()
                latitude = coords[0]
                longitude = coords[1]

            except (AttributeError, IndexError):
                print('[Coordinates not found] ' + str(coords) + ' Try to update "mobile_agent"')
                continue

            print(latitude, longitude)
            try:
                kml.newpoint(name=description,
                             coords=[(float(longitude), float(latitude))])
            except ValueError:
                print('[Invalid coordinates]')

    output = './maps/' + labelName + '.kml'
    print('saving results to ' + output)

    if not os.path.exists('./maps/'):
        os.makedirs('./maps/')

    kml.save(output)
