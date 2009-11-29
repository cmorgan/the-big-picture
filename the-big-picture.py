from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree import ElementTree
from BeautifulSoup import BeautifulSoup
import os
import datetime
import ctypes
import Image
import sys
import random
import logging

def set_wallpaper(wallpapers):
    im = Image.open(wallpapers)
    im.save("wallpaper.bmp")
    MY_WALLPAPER = "wallpaper.bmp"
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, MY_WALLPAPER , 0)

class ElementWrapper:
    def __init__(self, element):
        self._element = element
    def __getattr__(self, tag):
        if tag.startswith("__"):
            raise AttributeError(tag)
        return self._element.findtext(tag)

class RSSWrapper(ElementWrapper):
    def __init__(self, feed):
        channel = feed.find("channel")
        ElementWrapper.__init__(self, channel)
        self._items = channel.findall("item")

    def __getitem__(self, index):
        return ElementWrapper(self._items[index])



def getstuff(file_name,file_mode,base_url):
    LOG_FILENAME = os.getcwd() + '/log.txt'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    # create the url and the request
    url = base_url + file_name
    req = Request(url)
    # Open the url
    try:
        f = urlopen(req)
        # Open our local file for writing
        local_file = open(file_name, "w" + file_mode)   
        # Write to our local file
        local_file.write(f.read())
        local_file.close
        logging.debug(str(datetime.datetime.now()) + ',' + file_name)
        print "logged"
    # handle errors
    except HTTPError, e:
        print "HTTP Error:",e.code , url
    except URLError, e:
            time.sleep(20)
            getstuff(file_name,file_mode,base_url)
 
def main():


    debug = False
    URL = "http://www.boston.com/bigpicture/index.xml"

    tree = ElementTree.parse(urlopen(URL))
    feed = RSSWrapper(tree.getroot())
    # Below shows the RSSWrapper in action---
    '''
    print "FEED", repr(feed.title)
    for item in feed:
        print "ITEM", repr(item.title), item.description
    '''
    item = feed[0]
    page = BeautifulSoup(item.description)

    anchors = page.findAll('img')
    links = []

    for a in anchors:
        links.append(a['src'])


    split = os.path.split(links[0])
    head = split[0]
    fname = split[1]

    # +-+-+-+- if fname is in directory set that as wall paper instead
    path=os.getcwd()
#    "C:\\somedirectory"  # insert the path to the directory of interest
    dirList=os.listdir(path)
    if fname in dirList:
        set_wallpaper(fname)
    else:
        pic = getstuff(fname,'b',head + '/')
        set_wallpaper(fname)
    
    if debug:
        print page.prettify()
        print links[0]
        print "using cache"
        print fname

if __name__ == "__main__": main()
