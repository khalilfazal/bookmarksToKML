# -*- coding: utf-8 -*-
"""
Go to Google Bookmarks: https://www.google.com/bookmarks/

On the bottom left, click "Export bookmarks": https://www.google.com/bookmarks/bookmarks.html?hl=en

After downloading the html file, run this script on it to generate a KML.

"""

from lxml.html import document_fromstring
import simplekml

from urllib import FancyURLopener

import os
import random
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

class Browser(FancyURLopener):
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
    ]

    version = random.choice(user_agents)

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

            browser = Browser()

            if coords_in_url.search(url):
                # Coordinates are in URL itself
                latitude = coords_in_url.search(url).groups()[0]
                longitude = coords_in_url.search(url).groups()[1]
            else:
                # Load map and find coordinates in source of page
                sock = False

                while not sock:
                    try:
                        sock = browser.open(url.replace(' ','+'))
                    except Exception, e:
                        print 'Connection problem:'
                        print repr(e)
                        print 'Retrying randomly between 15 and 60 seconds.'
                        time.sleep(random.randint(15, 60))

                content = sock.read()
                sock.close()
                time.sleep(random.randint(15, 60)) # Don't annoy server
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
