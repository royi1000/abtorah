import os
import logging
import json
import requests
import argparse
from collections import defaultdict
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
    comment_handle = {'Tafsir Rasag': 'one_off_introduction',
                      'Rabbeinu Bahya': 'one_off_introduction',
                      'Iben Ezra on Lamentations': 'one_off_introduction',
                      'Ralbag on Song of Songs': 'one_off_introduction',
                      'Tur HaAroch': 'one_off_introduction',
                      'Tosafot Yom Tov': 'one_off_introduction_check', # not always introduction
                      'Targum of I Chronicles': 'ignore',
                      'Targum of II Chronicles': 'ignore',
                      'Targum Neofiti': 'neofiti',  # only first genesis chapter,
                      # 'Abarbanel on Torah': 'one_to_one',
                      # 'Bekhor Shor': 'one_to_one',
                      # 'Chizkuni': 'one_to_one',
                      # 'Minchat Shai': 'one_to_one',
                      'Ralbag': 'one_to_one',
                      # 'Gra on Pirkei Avot': 'one_to_one',
                      # 'Lechem Shamayim': 'one_to_one',
                      # 'Rabbeinu Yonah on Pirkei Avot': 'one_to_one',

                      # 'Rif': 'one_to_one',
                      # 'Rashba': 'one_to_one',
                      # 'Chidushei Agadot': 'one_to_one',
                      # 'Chidushei Halachot': 'one_to_one',
                      # 'Maharam Shif': 'one_to_one',
                      # 'Pilpula Charifta': 'one_to_one',
                      # 'Ramban': 'one_to_one',
                      # 'Ritva': 'one_to_one',
                      # 'Rosh': 'one_to_one',
                      # 'Shita Mekubetzet': 'one_to_one',
                      'Biur Halacha': 'one_to_one',

                      'Gur Aryeh': 'one_to_one_gur',
                      'Harchev Davar': 'one_to_one_gur',
                      'Siftei Hakhamim': 'one_to_one_gur',
                      'JPS': 'not_direct',
                      'Meshech Hochma': 'not_direct',
                      'Penei David': 'not_direct',
                      'Akeidat Yitzchak': 'not_direct',
                      'Rambam Introduction to Masechet Horayot': 'not_direct',
                      'Rambam Introduction to Seder Kodashim': 'not_direct',
                      'Boaz': 'not_direct',
                      'Yachin': 'not_direct',
                      'Divrey Chamudot': 'not_direct',
                      'Korban Netanel': 'not_direct',
                      'Maadaney Yom Tov': 'not_direct',
                      'Tiferet Shmuel': 'not_direct',
                      'Yad Ramah': 'not_direct',
                      'Commentary on Sefer Hamitzvot of Rasag': 'not_direct',
                      'Hasagot HaRamban al Sefer HaMitzvot': 'not_direct',

                      'Shney Luchot HaBrit': 'complex_shnei',  # parash and paragraph (Shney Luchot HaBrit, Bereshit, Derech Chaim Tochachot Musar)

                      }

    def __init__(self, host=DEFAULT_HOST):
        self.host = host
        _toc = requests.get(host + self.TOC_PATH).text
        self.toc = json.loads(_toc)
        self.map = {}
        self.comment_map = defaultdict(list)
        self.counter = 1
        self.json_dir = '/tmp/json'

    def check(self, items):
        for item in items:
            if "category" in item:
                self.check(item[u'contents'])
            else:
                #  item title have priority
                if (item.get('collectiveTitle') not in self.comment_handle) and (item["title"] not in self.comment_handle):
                    if "base_text_mapping" in item:
                        if item["base_text_mapping"]:
                            if item["base_text_titles"][0].replace('_', ' ') not in item["firstSection"]:
                                logger.warning("item: {}, base:{} not in first: {}".
                                               format(item['title'], item["base_text_titles"][0], item["firstSection"]))
                                raise
                        else:
                            logger.info("no base mapping item: {} -- first:{} ++ titles:{}".
                                        format(item['title'],
                                               item["firstSection"],item.get("base_text_titles")))
                            f = item["firstSection"]
                            if ':' not in f[-3:] and not f[-1] == '1' and \
                                    not (f[-2].isdigit() and (f[-1] in ['a', 'b'])):
                                raise

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
                if item['category'] in ['Targum Neofiti']:
                    logger.warning("skipped: {}".format(item['category']))
                    continue
                self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
                                                                       item[u'heCategory'].
                                                                       encode('utf-8').replace('"', "''"),
                                                                       item[u'category']))
                self.walk_on_items(item[u'contents'], level+1)
                self.toc_file.write('{}</node>\n'.format(' ' * 4 * level))
            else:  # real book
                title, he_title = item["title"], item["heTitle"]
                if not item["dependence"]:  # not commentary
                    continue
                    book = self.get_book(item["firstSection"], chapter=None)
                    if book["isComplex"]:
                        self.handle_complex_book(book, level)
                    else:
                        book = self.get_book(title, all=True)
                        self.handle_simple_book(book, level)
                else:
                    book = self.get_book(item["firstSection"], chapter=None)
                    if item["base_text_titles"]:
                        base_text_titles = item["base_text_titles"]
                        if title in ['Targum of I Chronicles', 'Targum of II Chronicles']:
                            base_text_titles = [title.split('of')[1][1:]]

                        if title in ['Akeidat Yitzchak', 'Penei David', 'JPS',
                                     'Penei David']:  # not direct commentary
                            if book["isComplex"]:
                                self.handle_complex_book(book, level)
                            else:
                                book = self.get_book(title, all=True)
                                self.handle_simple_book(book, level)
                            for base in base_text_titles:
                                self.comment_map[base].append((title, 'not_direct'))
                            continue

                        if len(base_text_titles) > 1 and title != item['collectiveTitle']:
                            logger.info("category: {} {}".format(title, he_title.encode('utf-8')))
                            self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
                                                                                   he_title.
                                                                                   encode('utf-8').replace('"', "''"),
                                                                                   title))
                        first_section = item['firstSection']
                        if first_section.endswith('Introduction'):
                            self.handle_simple_book(book, level+1)
                            first_section = book['next']

                        if not item.get('base_text_mapping') and item['firstSection'].endswith('1:1'):
                            item["base_text_mapping"] = "many_to_one"
                        assert (item["base_text_mapping"])
                        if base_text_titles[0] in first_section:
                            start = first_section.split(base_text_titles[0])[0]
                            for base in base_text_titles:
                                self.comment_map[base].append((title, item['base_text_mapping']))
                                book = self.get_book("{}{}".format(start, base), all=True)
                                self.handle_simple_book(book, level+1)
                        else:
                            raise item

                        if len(base_text_titles) > 1 and title != item['collectiveTitle']:
                            self.toc_file.write('{}</node>\n'.format(' ' * 4 * level))

                    #import pdb; pdb.set_trace()
                    else:
                        logger.error("unknown commentary type: {} firstSection: {} base_text_mapping".
                                     format(title, item["firstSection"], item["base_text_mapping"]))
                        raise item

    def handle_complex_book(self, book, level):
        length = 0
        book_json = dict(he=[], en=[], chapter_he=[], chapter_en=[])
        title = book["indexTitle"]
        he_title = book["heIndexTitle"]
        while book:
            length += 1
            book_json['chapter_en'].append(book['book'])
            book_json['chapter_he'].append(book['heTitle'])
            book_json['he'].append(book['he'])
            book_json['en'].append(book.get('en', []))
            if not book['next']:
                book = None
            else:
                book = self.get_book(book["next"], chapter=None)
        book_json['length'] = length
        self.toc_file.write('{}<node n="{}" en="{}" i="{}" c="{}" t="2">\n'.
                        format(' ' * 4 * level,
                               he_title.encode('utf-8').replace('"', "''"),
                               title, self.counter, length))
        self.map[book['text']] = self.counter
        self.write_book(book_json, self.counter)
        self.counter += 1

    def handle_simple_book(self, book, level):
        book_json = {}
        l = 0
        if 'lengths' in book:
            l = book['lengths'][0]

        book_json['en'] = book['text']
        book_json['he'] = book['he']
        title = book['book']
        he_title = book['heTitle']
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
        self.toc_file.write('{}<node n="{}" en="{}" i="{}" c="{}" t="1">\n'.
                            format(' ' * 4 * level,
                                   he_title.encode('utf-8').replace('"', "''"),
                                   title, self.counter, length))
        self.map[title] = self.counter
        self.write_book(book_json, self.counter)
        self.counter += 1

    def write_book(self, data, _id):
        open('{}/{}.json'.format(self.json_dir, _id), 'w+').write(json.dumps(data, indent=1))

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", help="check validity of direct commenters",
                        action="store_true", dest="check")
    args = parser.parse_args()
    sef_logger()
    toc = TOC()
    if args.check:
        toc.check(toc.toc)
    else:
        toc.walk_on_toc()
