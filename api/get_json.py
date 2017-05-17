import os
import logging
import json
import requests
from collection import defaultdict
from colorlog import ColoredFormatter

logging.basicConfig()
logger = logging.Logger(__name__, logging.INFO)

not_native_comment = []
native_comment = []

#               "firstSection": "Biur Halacha 1:1",
#                "base_text_mapping": "commentary_increment_base_text_depth",
#                "title": "Biur Halacha",

def sef_logger():
    color_formatter = ColoredFormatter("%(log_color)s %(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s")
    sh = logging.StreamHandler()
    sh.setFormatter(color_formatter)
    logger.addHandler(sh)
    logger.info("Logger Initialized")

DEFAULT_HOST = "http://www.sefaria.org"


class TOC(object):
    TOC_PATH = "/api/index/"
    TEXT_PATH = "/api/texts/"
    NO_TEXT = "with_text=0"
    NO_COMMENT = "commentary=0"
    ALL_BOOK = "pad=0"

    def __init__(self, host=DEFAULT_HOST):
        self.host = host
        _toc = requests.get(host + self.TOC_PATH).text
        self.toc = json.loads(_toc)
        self.map = {}
        self.comment_map = defaultdict(list)
        self.counter = 1
        self.json_dir = '/tmp/json'

    def walk_on_toc(self, toc_file_name="toc.xml"):
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
        self.toc_file = open(self.json_dir + '/' + toc_file_name, 'w+')
        self.toc_file.write('<?xml version="1.0" ?>\n<index name="onyourway">\n')
        self.walk_on_items(self.toc)
        self.toc_file.write('</index>')

    def walk_on_items(self, items, level=0):
        for item in items:
            if "category" in item:
                logger.info("category: {} {}".format(item["category"], item["heCategory"].encode('utf-8')))
                self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
                                                                       item[u'heCategory'].
                                                                       encode('utf-8').replace('"', "''"),
                                                                       item[u'category']))
                self.walk_on_items(item[u'contents'], level+1)
                self.toc_file.write('{}</node>\n'.format(' ' * 4 * level))
            else:  # real book
                title, he_title = item["title"], item["heTitle"]
                if not item["dependence"]:
                    book = self.get_book(item["title"], all=True)
                    if book["isComplex"]:
                        self.handle_complex_book(book)
                    else:
                        self.handle_simple_book(book)
                else:
                    if title in native_comment:
                        for b in book["base_text_titles"]:
                            self.map[b].append(title)
                    #import pdb; pdb.set_trace()
                    else:
                        logger.error("unknown commentary type: {} firstSection: {} base_text_mapping".
                                     format(title, item["firstSection"], item["base_text_mapping"]))
                self.counter += 1

    def handle_complex_book(self, book):
        length = 1
        while book["next"]

    def handle_simple_book(self, book):
        book_json = {}
        l = 0
        if 'lengths' in book:
            l = book['lengths'][0]

        book_json['en'] = book['text']
        book_json['he'] = book['he']
        length = max(len(book['text']), len(book['he']))
        if l > length:
            raise IndexError("book {} length error len: {} en: {} he: {}".format(title, l,
                                                                                 len(book['text']),
                                                                                 len(book['he'])))
        elif length > l:
            logger.warning("book {} length incorrect len: {} en: {} he: {}".format(title, l,
                                                                                   len(book['text']),
                                                                                   len(book['he'])))
        length = max(l, length)
        book_json['length'] = length
        self.toc_file.write('{}<node n="{}" en="{}" i="{}" c="{}" m="1">\n'.
                            format(' ' * 4 * level,
                                   he_title.encode('utf-8').replace('"', "''"),
                                   title, self.counter, length))
        self.map[book['text']: self.counter]
        self.write_book(book_json, self.counter)

    def write_book(self, data, id):
        open('{}/{}.json'.format(self.json_dir, id), 'w+').write(json.dumps(data, indent=1))

    def get_book(self, book, chapter=(1, ), all=False, commentary=False, text=True):
        attrs = []
        if all:
            attrs.append(self.ALL_BOOK)
        if not commentary:
            attrs.append(self.NO_COMMENT)
        if not text:
            attrs.append(self.NO_TEXT)
        url = self.host+self.TEXT_PATH+book
        if chapter and not all:
            c = '.'.join(chapter)
            url = url + ' ' + c
        if attrs:
            a = '&'.join(attrs)
            url = url + '?' + a
        logger.info(url)
        return json.loads(requests.get(url).text)

if __name__ == '__main__':
    sef_logger()
    toc = TOC()
    toc.walk_on_toc()