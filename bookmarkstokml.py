# -*- coding: utf-8 -*-
"""
Go to Google Bookmarks: https://www.google.com/bookmarks/

On the bottom left, click "Export bookmarks": https://www.google.com/bookmarks/bookmarks.html?hl=en

After downloading the html file, run this script on it to generate a KML.

"""

from lxml.html import document_fromstring
import simplekml

from urllib2 import urlopen

import os
import re
import sys
import time

# filename = r'GoogleBookmarks.html'
filename = sys.argv[1]

with open(filename) as bookmarks_file:
    data = bookmarks_file.read()

# kml = simplekml.Kml()

# Hacky and doesn't work for all of the stars:
lat_re = re.compile('markers:[^\]]*latlng[^}]*lat:([^,]*)')
lon_re = re.compile('markers:[^\]]*latlng[^}]*lng:([^}]*)')
coords_in_url = re.compile('\?q=(-?\d{,3}\.\d*),\s*(-?\d{,3}\.\d*)')

doc = document_fromstring(data)

for label in doc.body.iterfind('dl/dl/h3'):
    labelName = label.text_content()
    #print labelName

    kml = simplekml.Kml()
    kml.document.name = labelName

    for element, attribute, url, pos in label.getnext().iterlinks():
        if 'maps.google' in url:
            description = element.text or ''
            print description.encode('UTF8')
            print "URL: {0}".format(url)

            if coords_in_url.search(url):
                # Coordinates are in URL itself
                latitude = coords_in_url.search(url).groups()[0]
                longitude = coords_in_url.search(url).groups()[1]
            else:
                # Load map and find coordinates in source of page
                try:
                    sock = urlopen(url.replace(' ','+'))
                except Exception, e:
                    print 'Connection problem:'
                    print repr(e)
                    print 'Waiting 2 minutes and trying again'
                    time.sleep(120)
                    sock = urlopen(url.replace(' ','+'))
                content = sock.read()
                sock.close()
                time.sleep(3) # Don't annoy server
                try:
                    latitude = lat_re.findall(content)[0]
                    longitude = lon_re.findall(content)[0]
                except IndexError:
                    print '[Coordinates not found]'
                    print
                    continue

            print latitude, longitude
            try:
                kml.newpoint(name=description,
                             coords=[(float(longitude), float(latitude))])
            except ValueError:
                print '[Invalid coordinates]'
            print

    kml.save("./maps/" + labelName + ".kml")
