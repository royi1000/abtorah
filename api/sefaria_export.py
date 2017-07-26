# coding=utf-8

import os
import shutil
import logging
import json
import argparse
from collections import defaultdict
from colorlog import ColoredFormatter

logging.basicConfig()
logger = logging.Logger(__name__, logging.DEBUG)

en_file = '/English/merged.json'
he_file = '/Hebrew/merged.json'

tanach_list = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "I Samuel", "II Samuel",
               "I Kings", "II Kings", "Jeremiah", "Ezekiel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
               "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Psalms", "Proverbs", "Job",
               "Song of Songs", "Ruth", "Lamentations", "Ecclesiastes", "Esther", "Daniel", "Ezra", "Nehemiah",
               "I Chronicles", "II Chronicles",
                ]
torah_list = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
# noe to one dict +key comment
complex_commentary = ["Abarbanel on Torah", "Tur HaAroch", "Avi Ezer", "Bekhor Shor", "Chizkuni",
                      "Minchat Shai on Torah", "Rabbeinu Bahya", "Siftei Hakhamim", "Marganita Tava al Sefer Hamitzvot",
                      "Megilat Esther al Sefer Hamitzvot", "Kinaat Sofrim al Sefer Hamitzvot", "Raavad on Sefer Yetzirah",
                      "Marpeh la'Nefesh", "Pat Lechem", "Tov haLevanon"]

not_direct_commentary = ["Akeidat Yitzchak", "Meshech Hochma", "Penei David", "Shney Luchot HaBrit",
                         "Rambam Introduction to Masechet Horayot", "Divrey Chamudot",
                         "Commentary on Sefer Hamitzvot of Rasag"]

collective_not_direct_commentary = ["Rif", "Yachin", "Boaz", "Divrey Chamudot", "Maadaney Yom Tov",
                                    "Pilpula Charifta", 'Rosh', "Korban Netanel", "Tiferet Shmuel", "Yad Ramah"]
perek_commentarry = []
perek_commentarry_title = ['Chiddushei Ramban', "Shita Mekubetzet on Ketubot", "Shita Mekubetzet on Nedarim",
                           "Shita Mekubetzet on Nazir", "Shita Mekubetzet on Sotah", "Shita Mekubetzet on Bava Kamma",
                           "Shita Mekubetzet on Bava Metzia", "Shita Mekubetzet on Bava Batra", ]
perek_commentarry_collective = ["Rashba", "Chidushei Agadot", "Chidushei Halachot", "Chokhmat Shlomo", "Maharam",
                                "Maharam Shif", 'Ritva', "Tosafot Rid"]

one_on_one_titles = ["Binyan Yehoshua on Avot D'Rabbi Natan", 'Commentary of Chida on Tractate Gerim',
                    "Haggahot Ya'avetz on Avot D'Rabbi Natan", "Haggahot Ya'avetz on Tractate Derekh Eretz Rabbah",
                    'Nahalat Yaakov on Tractate Gerim', 'Nahalat Yaakov on Tractate Kallah',
                    'Nahalat Yaakov on Tractate Derekh Eretz Rabbah', 'New Nuschah on Tractate Gerim',
                    "Rishon Letzion on Avot D'Rabbi Natan", "Tumat Yesharim on Avot D'Rabbi Natan",
                    'HaGra on Sefer Yetzirah Gra Version', "Pri Yitzhak on Sefer Yetzirah Gra Version",
                    'Rasag on Sefer Yetzirah'
                    ]

known_sections = {
    (u'Chapter', u'Verse'): [[u'Chapter', u'Verse'], ["פרק", "פסוק"]],
    (u'Perek', u'Passuk'): [[u'Chapter', u'Verse'], ["פרק", "פסוק"]],
    (u'Chapter', u'Verse', u'Comment'): [[u'Chapter', u'Verse', u'Comment'], ["פרק", "פסוק", "פירוש"]],
    (u'Chapter', u'Verse', u'Paragraph'): [[u'Chapter', u'Verse', u'Paragraph'], ["פרק", "פסוק", "פסקה"]],
    (u'Chapter', u'Section'): [[u'Chapter', u'Section'], ["פרק", "חלק"]],
    (u'Gate', u'Paragraph'): [[u'Gate', u'Paragraph'], ["שער", "פסקה"]],
    (u'Chapter', u'Mishna'): [[u'Chapter', u'Mishna'], ["פרק", "משנה"]],
    }

flat_sections = ["Chapter", "Gate"]


def sef_logger():
    color_formatter = ColoredFormatter("%(log_color)s %(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s")
    sh = logging.StreamHandler()
    sh.setFormatter(color_formatter)
    logger.addHandler(sh)
    logger.info("Logger Initialized")


def txt_in_partial_list(title, partial_title_list):
    return bool([1 for x in [(z in title) for z in partial_title_list] if x])


class TOC(object):
    DEFAULT_PATH = os.path.expanduser('~/Sefaria-Export')

    def __init__(self, export_path, dest_path):
        self.export_path = export_path
        self.toc = json.load(open(self.export_path+'/table_of_contents.json'))
        self.toc_data = defaultdict(dict)
        self.comment_map = defaultdict(list)
        self.counter = 1
        self.json_dir = dest_path
        self.toc_data["commentary"] = defaultdict(list)
        # for fast debug
        self.skip = False
        self.skip_title = "Biur Halacha"

    def walk_on_toc(self, toc_file_name="toc.xml"):
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
        self.toc_file = open(self.json_dir + '/' + toc_file_name, 'w+')
        self.toc_file.write('<?xml version="1.0" ?>\n<index name="onyourway">\n')
        self.walk_on_items(self.toc)
        self.toc_file.write('</index>')

    def walk_on_items(self, items, level=0, path='/json'):
        for item in items:
            if "category" in item:
                #logger.debug("category: {} {}".format(item["category"], item["heCategory"].encode('utf-8')))
                if item['category'] in ['Targum Neofiti']:
                    logger.warning("skipped: {}".format(item['category']))
                    continue
                self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
                                                                       item[u'heCategory'].
                                                                       encode('utf-8').replace('"', "''"),
                                                                       item[u'category']))
                self.walk_on_items(item[u'contents'], level+1, path=path+'/'+item['category'])
                self.toc_file.write('{}</node>\n'.format(' ' * 4 * level))
            else:  # real book
                title, he_title = item["title"], item["heTitle"]
                if self.skip and title != self.skip_title:
                    continue
                self.skip = False
                src_dir = self.export_path+path+'/'+title
                lang_type = 'both'
                if not os.path.isfile(src_dir+en_file) and not os.path.isfile(src_dir+he_file):
                    logger.error("missing lang, path: {}".format(src_dir))
                    continue
                elif not os.path.isfile(src_dir + he_file):
                    #logger.debug("missing he, path: {}".format(src_dir))
                    lang_type = 'en'
                elif not os.path.isfile(src_dir + en_file):
                    #logger.debug("missing en, path: {}".format(src_dir))
                    lang_type = 'he'
                length = 0
                langs = dict()
                he, en = None, None
                he_text, en_text = [], []
                schema = json.load(open("{}/schemas/{}.json".format(self.export_path, title.replace(' ', '_'))))
                is_complex = False
                if os.path.isfile(src_dir + he_file):
                    he = json.load(open(src_dir + he_file))
                    langs['he'] = (he, he["text"])
                    if "schema" in he:
                        is_complex = True
                    #shutil.copy(src_dir + he_file, "{}/{}.he.json".format(self.json_dir, self.counter))
                if os.path.isfile(src_dir + en_file):
                    en = json.load(open(src_dir + en_file))
                    langs['en'] = (en, en["text"])
                    if "schema" in en:
                        is_complex = True
                    #shutil.copy(src_dir + en_file, "{}/{}.en.json".format(self.json_dir, self.counter))
                if not is_complex:
                    sections = schema["schema"]["sectionNames"]
                    if tuple(sections) not in known_sections:
                        print '[',
                        for k in schema["schema"]["heSectionNames"]:
                            print unicode('"'+k+'",').encode('utf-8'),
                        print ']'

                        raise KeyError('title:{} unknown section: {} '.format(title, sections))
                    if sections[0] in flat_sections:
                        for lang in langs:
                            for chap, data in enumerate(langs[lang][1]):
                                length = max(length, chap+1)
                                json.dump(data, open("{}/{}.{}.{}.json".format(self.json_dir, self.counter,
                                                                               chap, lang), 'w+'))

                self.toc_file.write('{}<node n="{}" en="{}" i="{}" chaps="{}" lang="{}"/>\n'.
                                    format(' ' * 4 * level, he_title.
                                    encode('utf-8').replace('"', "''"),
                                    title,
                                    self.counter,
                                    length,
                                    lang_type))
                self.toc_data['hebrew_index'][self.counter] = he_title.encode('utf-8').replace('"', "''")
                self.toc_data['books_index'][self.counter] = title
                self.toc_data['reverse_index'][title] = self.counter
                self.counter += 1

    def walk_on_commentary(self, items=None):
        # comment types: 0 - one on one, 1 - one on one dict, 2 - not direct, 3 - one on one dict (empty string key),
        # 4 - hebrew dict (Bereshit instaed of Genesis), 5 - commentary to chapter level
        if items is None:
            items = self.toc
        for item in items:
            if "category" in item:
                if item['category'] in ['Targum Neofiti']:
                    logger.warning("skipped: {}".format(item['category']))
                    continue
                self.walk_on_commentary(item[u'contents'])
            else:  # real book
                if "dependence" not in item or not item["dependence"]:
                    continue
                title, he_title = item["title"], item["heTitle"]
                title_in = txt_in_partial_list(title, ["Gur Aryeh on ", "Harchev Davar on "])
                dict_comment_flag = False  # Sefaria complex text type
                if title in complex_commentary or title_in:
                    dict_comment_flag = True
                    item["base_text_mapping"] = "one_to_one"
                if title in ["Tur HaAroch"]:
                    item["base_text_titles"] = torah_list
                if title in one_on_one_titles or item.get('collectiveTitle') in ["Gra's Nuschah", "Haggahot", "Haggahot R' Yeshaya Berlin",
                              "Haggahot and Marei Mekomot", "Kisse Rahamim", "Mesorat HaShas", "Mitzpeh Etan",
                              "Kessef Mishneh", "Lev Sameach"]:
                    item["base_text_mapping"] = "one_to_one"
                if title in ["Shita Mekubetzet on Berakhot", 'Shita Mekubetzet on Beitzah']:
                    item["base_text_mapping"] = "one_to_one"
                    item["base_text_titles"] = [title.split('on ')[1]]
                if "Minchat Shai" in title and title != "Minchat Shai on Torah":
                    item["base_text_mapping"] = "one_to_one"
                if "Ba'er Hetev on Shulchan Arukh" in title:
                    item["base_text_mapping"] = "one_to_one"
                    item["base_text_titles"] = [title.split('on ')[1]]
                if title in ["Gra on Pirkei Avot", "Lechem Shamayim on Pirkei Avot", "Rabbeinu Yonah on Pirkei Avot"]\
                        or item.get("collectiveTitle") in perek_commentarry_collective \
                        or txt_in_partial_list(title, perek_commentarry_title):
                    item["base_text_mapping"] = "one_to_one"
                # if item["collectiveTitle"] == "Korban Netanel":
                #     for i in range(len(item["base_text_titles"])):
                #         item["base_text_titles"][i] = "Rosh on "+item["base_text_titles"][i]

                if item.get("base_text_mapping"):
                    if not len(item["base_text_titles"]) == 1:
                        if title in ["Tafsir Rasag", "Targum Jerusalem"] or dict_comment_flag:
                            comment_type = 1
                            if title in ["Rabbeinu Bahya"]:
                                comment_type = 4
                            for i in item["base_text_titles"]:
                                orig_id = self.toc_data["reverse_index"][i]
                                comment_id = self.toc_data["reverse_index"][title]
                                self.toc_data["commentary"][orig_id].append((comment_id, comment_type))
                            continue
                        else:
                            logger.error("invalid len base_text_titles: {} in: {}, mapping: {}".format(len(item["base_text_titles"]),
                                                                                               title,item["base_text_mapping"]))
                    orig_id = self.toc_data["reverse_index"][item["base_text_titles"][0].replace('_', ' ')]
                    comment_id = self.toc_data["reverse_index"][title]
                    self.toc_data["commentary"][orig_id].append((comment_id, 0))
                elif item.get("base_text_titles"):
                    if title in not_direct_commentary or item["collectiveTitle"] in collective_not_direct_commentary:
                        for i in item["base_text_titles"]:
                            orig_id = self.toc_data["reverse_index"][i]
                            comment_id = self.toc_data["reverse_index"][title]
                            self.toc_data["commentary"][orig_id].append((comment_id, 2))
                    elif title in ["Ibn Ezra on Lamentations", "Ralbag on Song of Songs", "Ralbag Ruth",
                                   "Ralbag Esther", "Magen Avot", "Haggahot Ya'avetz on Tractate Derekh Eretz Zuta",
                                   'Nahalat Yaakov on Tractate Derekh Eretz Zuta'] or \
                                    "Tosafot Yom Tov on" in title:
                        orig_id = self.toc_data["reverse_index"][item["base_text_titles"][0].replace('_', ' ')]
                        comment_id = self.toc_data["reverse_index"][title]
                        self.toc_data["commentary"][orig_id].append((comment_id, 3))
                    elif item['collectiveTitle']in perek_commentarry_collective or txt_in_partial_list(title,
                                                                                                       perek_commentarry_title):
                        orig_id = self.toc_data["reverse_index"][item["base_text_titles"][0].replace('_', ' ')]
                        comment_id = self.toc_data["reverse_index"][title]
                        self.toc_data["commentary"][orig_id].append((comment_id, 5))
                    else:
                        logger.warning(item)
                        self.verify_comment(item)
                        raise


                else:
                    if title not in ['JPS 1985 Footnotes'] and not bool([1 for x in [(z in title) for z in ['Rambam Introduction to', 'Tosafot Yom Tov Introduction']] if x]):
                        logger.warning(title)
                        raise

    def dump_toc_data(self):
        open(self.json_dir+'/main.json', 'w+').write(json.dumps(self.toc_data))

    def verify_comment(self, item):
        for i in item["base_text_titles"]:
            orig_id = self.toc_data["reverse_index"][i]
            comment_id = self.toc_data["reverse_index"][item["title"]]
            orig = json.load(open("{}/{}.he.json".format(self.json_dir, orig_id)))
            try:
                comment = json.load(open("{}/{}.he.json".format(self.json_dir, comment_id)))
            except IOError:
                comment = json.load(open("{}/{}.en.json".format(self.json_dir, comment_id)))
            f = open("/tmp/a.html", 'w+')
            f.write('<html><body><div dir="rtl" align="right">\n')
            logger.warning((orig_id, comment_id, item['title']))
            for ind, j in enumerate(orig['text']):
                for ind_inner, k in enumerate(j):
                    if type(k) is list:
                        k = '</br>'.join(k)
                    f.write("<b>{}-{}</b> {}</br>".format(ind, ind_inner, k.encode('utf-8')))
                    if (len(comment['text']) > ind) and len(comment['text'][ind]) > ind_inner:
                        txt = comment['text'][ind][ind_inner]
                        if type(txt) is list:
                            txt = '</br>'.join(txt)
                        f.write('</br><b>{}-{}</b><font size="5em">{}</font></br>'.format(ind, ind_inner,
                                                                             txt.encode('utf-8')))
                f.write("<hr>")
            f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", help="pdb on failure",
                        action="store_true", dest="debug")
    parser.add_argument("--json", help="get jsons from export",
                        action="store_true", dest="get_json")
    parser.add_argument("--sefaria-path", help="sefaria export path",
                        default=TOC.DEFAULT_PATH, dest="path")
    parser.add_argument("--dest-path", help="json dest",
                        default='/tmp/json', dest="dest")
    args = parser.parse_args()
    if args.debug:
        import autodebug

    sef_logger()
    toc = TOC(args.path, args.dest)
    # if args.get_json:
    toc.walk_on_toc()
    toc.walk_on_commentary()
    toc.dump_toc_data()
