import requests
import json

DEFAULT_HOST = "http://www.sefaria.org"

class TOC(object):
    TOC_PATH = "/api/index/"

    def __init__(self, host=DEFAULT_HOST):
        self.host = host
        _toc = requests.get(host + self.TOC_PATH).text
        self.toc = json.loads(_toc)
        self.counter = 1

    def walk_on_toc(self, toc_file_name="toc.xml"):
        self.toc_file = open(toc_file_name, 'w+')
        self.toc_file.write('<?xml version="1.0" ?>\n<index name="onyourway">\n')
        self.walk_on_items(self.toc)
        self.toc_file.write('</index>')

    def walk_on_items(self, items, level=0):
        for item in items:
            if "category" in item:
                print item["category"], item["heCategory"]
                self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
                                                          item[u'heCategory'].encode('utf-8').replace('"', "''"),
                                                          item[u'category']))
                self.walk_on_items(item[u'contents'], level+1)
                self.toc_file.write('{}</node>\n'.format(' ' * 4 * level))

if __name__ == '__main__':
    toc = TOC()
    toc.walk_on_toc()