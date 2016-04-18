V2016.04.17

Go to Google Bookmarks: https://www.google.com/bookmarks/

On the bottom left, click "Export bookmarks": https://www.google.com/bookmarks/bookmarks.html?hl=en

Install script dependencies:
pip3 install simplekml lxml

After downloading the html file, run this script on it to generate a KML file per bookmark label:
python3 bookmarkstokml.py GoogleBookmarks.html 

It's hacky and doesn't work on all of them, but it kinda works.
