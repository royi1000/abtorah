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
# one to one dict +key comment
complex_commentary = ["Alshich on Torah", "Abarbanel on Torah", "Tur HaAroch", "Avi Ezer", "Bekhor Shor", "Chizkuni",
                      "Minchat Shai on Torah", "Rabbeinu Bahya", "Siftei Hakhamim", "Marganita Tava al Sefer Hamitzvot",
                      "Megilat Esther al Sefer Hamitzvot", "Kinaat Sofrim al Sefer Hamitzvot", "Raavad on Sefer Yetzirah",
                      "Marpeh la'Nefesh", "Pat Lechem", "Tov haLevanon", "Mizrachi",
                      ]


not_direct_commentary = ["Akeidat Yitzchak", "Meshech Hochma", "Penei David", "Shney Luchot HaBrit",
                         "Rambam Introduction to Masechet Horayot", "Divrey Chamudot",
                         "Commentary on Sefer Hamitzvot of Rasag", "Darchei HaTalmud", 'Mordechai on Bava Batra',
                         'Brit Moshe']

collective_not_direct_commentary = ["Rif", "Yachin", "Boaz", "Divrey Chamudot", "Maadaney Yom Tov",
                                    "Pilpula Charifta", 'Rosh', "Korban Netanel", "Tiferet Shmuel", "Yad Ramah"]
perek_commentarry = []
perek_commentarry_title = ['Chiddushei Ramban', "Shita Mekubetzet on Ketubot", "Shita Mekubetzet on Nedarim",
                           "Shita Mekubetzet on Nazir", "Shita Mekubetzet on Sotah", "Shita Mekubetzet on Bava Kamma",
                           "Shita Mekubetzet on Bava Metzia", "Shita Mekubetzet on Bava Batra", ]
perek_commentarry_collective = ["Rashba", "Chidushei Agadot", "Chidushei Halachot", "Chokhmat Shlomo", "Maharam",
                                "Maharam Shif", 'Ritva', "Tosafot Rid", "Melechet Shlomo", "Zeroa Yamin"]

one_on_one_titles = ["Binyan Yehoshua on Avot D'Rabbi Natan", 'Commentary of Chida on Tractate Gerim',
                     "Haggahot Ya'avetz on Avot D'Rabbi Natan", "Haggahot Ya'avetz on Tractate Derekh Eretz Rabbah",
                     'Nahalat Yaakov on Tractate Gerim', 'Nahalat Yaakov on Tractate Kallah',
                     'Nahalat Yaakov on Tractate Derekh Eretz Rabbah', 'New Nuschah on Tractate Gerim',
                     "Rishon Letzion on Avot D'Rabbi Natan", "Tumat Yesharim on Avot D'Rabbi Natan",
                     'HaGra on Sefer Yetzirah Gra Version', "Pri Yitzhak on Sefer Yetzirah Gra Version",
                     'Rasag on Sefer Yetzirah', "Ketzot HaChoshen on Shulchan Arukh, Choshen Mishpat",
                     "Me'irat Einayim on Shulchan Arukh, Choshen Mishpat", "Be'er HaGolah",
                    ]

# 3
complex_commentary_empty_string = ["Ibn Ezra on Lamentations", "Ralbag on Song of Songs", "Ralbag Ruth",
                                   "Ralbag Esther", "Magen Avot", "Haggahot Ya'avetz on Tractate Derekh Eretz Zuta",
                                   'Nahalat Yaakov on Tractate Derekh Eretz Zuta', "Ibn Ezra on Isaiah",
                                   "Netivot HaMishpat, Beurim on Shulchan Arukh, Choshen Mishpat",
                                   "Beur HaGra on Shulchan Arukh, Choshen Mishpat",
                                   "Netivot HaMishpat, Hidushim on Shulchan Arukh, Choshen Mishpat",
                                   "Pithei Teshuva on Shulchan Arukh, Choshen Mishpat", "Siftei Kohen on Shulchan Arukh, Choshen Mishpat"]

add_base_title_from_on = ["Shita Mekubetzet on Berakhot", 'Shita Mekubetzet on Beitzah',
                          "Be'er HaGolah on Shulchan Arukh, Choshen Mishpat", "Ketzot HaChoshen on Shulchan Arukh, Choshen Mishpat",
                          "Me'irat Einayim on Shulchan Arukh, Choshen Mishpat", "Netivot HaMishpat, Beurim on Shulchan Arukh, Choshen Mishpat",
                          "Netivot HaMishpat, Hidushim on Shulchan Arukh, Choshen Mishpat", "Pithei Teshuva on Shulchan Arukh, Choshen Mishpat",
                          "Siftei Kohen on Shulchan Arukh, Choshen Mishpat"]

known_sections = {
    (u'Chapter', u'Verse'): [[u'Chapter', u'Verse'], ["פרק", "פסוק"]],
    (u'Chapter', u'Paragraph', u'Comment'): [[u'Chapter', u'Paragraph', u'Comment'], ["פרק", "פסקה", "פירוש"]],
    (u'Perek', u'Passuk'): [[u'Chapter', u'Verse'], ["פרק", "פסוק"]],
    (u'Chapter', u'Verse', u'Comment'): [[u'Chapter', u'Verse', u'Comment'], ["פרק", "פסוק", "פירוש"]],
    (u'Chapter', u'Verse', u'Paragraph'): [[u'Chapter', u'Verse', u'Paragraph'], ["פרק", "פסוק", "פסקה"]],
    (u'Chapter', u'Section'): [[u'Chapter', u'Section'], ["פרק", "חלק"]],
    (u'Gate', u'Paragraph'): [[u'Gate', u'Paragraph'], ["שער", "פסקה"]],
    (u'Chapter', u'Mishna'): [[u'Chapter', u'Mishna'], ["פרק", "משנה"]],
    (u'Chapter', u'Mishna', u'Comment'): [[u'Chapter', u'Mishna', u'Comment'], ["פרק", "משנה", "פירוש"]],
    (u'Chapter', u'Mishnah', u'Comment'): [[u'Chapter', u'Mishna', u'Comment'], ["פרק", "משנה", "פירוש"]],
    (u'Perek', u'Mishna', u'Comment'): [[u'Chapter', u'Mishna', u'Comment'], ["פרק", "משנה", "פירוש"]],
    (u'Perek', u'Mishnah', u'Comment'): [[u'Chapter', u'Mishna', u'Comment'], ["פרק", "משנה", "פירוש"]],
    (u'Paragraph', ): [[u'Paragraph'], ["פסקה"]],
    (u'Section', u'Paragraph'): [[u'Gate', u'Paragraph'], ["חלק", "פסקה"]],
    (u'Chapter', u'comment'): [[u'Chapter', u'comment'], ["פרק", "פירוש"]],
    (u'Perek', u'Mishnah', u'Paragraph'): [[u'Chapter', u'Mishna', u'Paragraph'], ["פרק", "משנה", "פסקה"]],
    (u'Chapter', u'Seif', u'Comment'): [[u'Chapter', u'Paragraph', u'Comment'], ["פרק", "סעיף", "פירוש"]],
    (u'Daf', u'Line'): [[u'Page', u'Line'], ["דף", "שורה"]],
    (u'Siman', u'Paragraph'): [[u'Siman', u'Paragraph'], ["סימן", "פסקה"]],
    (u'Daf', u'Peirush'): [[u'Page', u'Comment'], ["דף", "פירוש"]],
    (u'Daf', u'Comment'): [[u'Page', u'Comment'], ["דף", "פירוש"]],
    (u'Daf', u'Paragraph'): [[u'Page', u'Paragraph'], ["דף", "פסקה"]],
    (u'Siman',): [[u'Siman'], ["סימן"]],
    (u'Seif', u'siman'): [[u'Siman', u'Seif', ], ["סימן", "סעיף"]],
    (u'Daf', u'Line', u'Comment'): [[u'Page', u'Line', u'Comment'], ["דף", "שורה", "פירוש"]],
    (u'Perek', u'Halacha', u'Siman'): [[u'Chapter', u'Halacha', u'Siman'], ["פרק", "הלכה", "סימן"]],
    (u'Halacha', u'Siman'): [[u'Halacha', u'Siman'], ["הלכה", "סימן"]],
    (u'Daf', u'Halakhah'): [[u'Page', u'Halacha'], ["דף", "הלכה"]],
    (u'Chapter', u'Paragraph'): [[u'Chapter', u'Paragraph'], ["פרק", "פסקה"]],
    (u'Parasha', u'Perek', u'Midrash'): [[u'Chapter', u'Verse', u'Midrash'], ["פרק", "פסוק", "מדרש"]],
    (u'Chapter', u'Piska'): [[u'Chapter', u'Paragraph'], ["פרק", "פסקה"]],
    (u'Volume', u'Chapter', u'Paragraph'): [[u'Volume', u'Chapter', u'Paragraph'], ["כרך", "פרק", "פסקה"]],
    (u'Perek', u'Pasuk'): [[u'Chapter', u'Verse'], ["פרק", "פסוק"]],
    (u'Perek', u'Pasuk'): [[u'Chapter', u'Verse'], ["פרק", "פסוק"]],
    (u'Psalm', u'Comment'): [[u'Chapter', u'Comment'], ["פרק", "פירוש"]],
    (u'Piska', u'Ot') : [[u'Chapter', u'Paragraph'], ["פסקא", "אות"]],
    (u'Perek', u'Paragraph'): [[u'Chapter', u'Paragraph'], ["פרק", "פסקה"]],
    (u'Remez', u'Paragraph'): [[u'Remez', u'Paragraph'], ["רמז", "פסקה"]],
    (u'Perek', u'Pasuk', u'Paragraph'): [[u'Chapter', u'Verse', u'Paragraph'], ["פרק", "פסוק", "פסקה"]],
    (u'Piska', u'Paragraph'): [[u'Chapter', u'Paragraph'], ["", "פסקה"]],
    (u'Perek', u'Pasuk', u'Comment'): [[u'Chapter', u'Verse', u'Comment'], ["פרק", "פסוק", "פירוש"]],
    (u'Chapter', u'Tosefta'): [[u'Chapter', u'Tosefta'], ["פרק", "תוספתא"]],
    (u'Chapter', u'Halakhah'): [[u'Chapter', u'Halacha'], ["פרק", "הלכה"]],
    (u'Chapter', u'Halakhah', u'Comment'): [[u'Chapter', u'Halacha', u'Comment'], ["פרק", "הלכה", "פירוש"]],
    (u'Mitzvah',): [[u'Commandment'], ["מצוה"]],
    (u'Chapter', u'Halacha'): [[u'Chapter', u'Halacha'], ["פרק", "הלכה"]],
    (u'Chapter', u'Halacha', u'Comment'): [[u'Chapter', u'Halacha', u'Comment'], ["פרק", "הלכה", "פירוש"]],
    (u'Siman', u"Se'if"): [[u'Siman', u"Seif"], ["סימן", "סעיף"]],
    (u'Siman', u'Seif Katan'): [[u'Siman', u'Seif Katan'], ["סימן", "סעיף קטן"]],
    (u'Siman', u"Se'if Katan"): [[u'Siman', u"Seif Katan"], ["סימן", "סעיף קטן"]],
    (u'Siman', u'Seif'): [[u'Siman', u'Seif'], ["סימן", "סעיף"]],
    (u'Siman', u'Seif', u'Paragraph'): [[u'Siman', u'Seif', u'Paragraph'], ["סימן", "סעיף", "פסקה"]],
    (u'Siman', u'Seif', u'Comment'): [[u'Siman', u'Seif', u'Comment'], ["סימן", "סעיף", "פירוש"]],
    (u'Siman', u"Se'if", u'Comment'): [[u'Siman', u"Seif", u'Comment'], ["סימן", "סעיף", "פירוש"]],
    (u'פרק', u"סעיף"): [[u'Paragraph', u"Seif"], ["סימן", "סעיף"]],
    (u'Chelek', u'Siman', u"Se'if") : [[u'Part', u'Siman', u"Seif"], ["חלק", "סימן", "סעיף"]],
    (u'Chelek', u'Siman', u'Seif'): [[u'Part', u'Siman', u'Seif'], ["חלק", "סימן", "סעיף"]],
    (u"Sha'ar", u'paragraph'): [[u"Gate", u'paragraph'], ["שער", "פסקה"]],
    (u'Chapter', u'Law') : [ [u'Chapter', u'Halacha'] , [ "פרק", "הלכה"]],
    (u'Book', u'Chapter', u'Section'): [[u'Book', u'Chapter', u'Section'], ["ספר", "פרק", "חלק"]],
    (u'Volume', u'Daf', u'Paragraph'): [[u'Volume', u'Page', u'Paragraph'], ["כרך", "דף", "פסקה"]],
    (u'Number',): [[u'Seif'], ["סעיף"]],  # Da'at Tevunoth
    (u'Section',): [[u'Section'], ["חלק"]],
    (u'Parsha', u'Paragraph'): [[u'Parsha', u'Paragraph'], ["פרשה", "פסקה"]],
    (u'Heichal', u"Sha'ar", u'Paragraph') : [ [u'Heichal', u"Sha'ar", u'Paragraph'] , [ "היכל", "שער", "פסקה"]],
    (u"Se'if",): [[u"Seif"], ["סעיף"]],
    (u'Chapter', u'Comment'): [[u'Chapter', u'Comment'], ["פרק", "פירוש"]],
    (u'Chapter', u'Mishnah'): [[u'Chapter', u'Mishna'], ["פרק", "משנה"]],
    (u'Line',): [[u'Line'], ["שורה"]],
    (u'Liturgy',): [[u'Line'], ["שורה"]],
    (u'Hadran',): [[u'Line'], ["שורה"]],
    (u'section',): [[u'Section'], ["פסקה"]],
    (u'Verse', u'Verset'): [[u'Verse', u'Verset'], ["בית", "שורה"]],
    (u'Perek', u'Line'): [[u'Chapter', u'Line'], ["פרק", "שורה"]],
    (u'Day of Week', u'Section'): [[u'Day', u'Section'], ["יום", "חלק"]],
    (u'Psalm',): [[u'Paragraph'], ["פסקה"]],
    (u'Paragraphs',): [[u'Paragraph'], ["פסקה"]],
    (u'Drush', u'Paragraph'): [[u'Drush', u'Paragraph'], ["דרוש", "פסקה"]],
    (u'Letter', u'Paragraph'): [[u'Letter', u'Paragraph'], ["אות", "פסקה"]],
    (u'Volume', u'Section', u'Teaching', u''): [[u'Volume', u'Section', u'Teaching', u''], ["כרך", "חלק", "פסקה", ""]],
    (u'Essay', u'Statement'): [[u'Essay', u'Statement'], ["מאמר", "ציטוט"]],
    (u'Kovetz', u'Paragraph', u'Segment '): [[u'Kovetz', u'Paragraph', u'Segment '], ["קובץ", "פסקה", "", ]],
    (u'Parashah', u'Torah', u'Section'): [[u'Parsha', u'Torah', u'Section'], ["פרשה", "תורה", "חלק"]],
    (u'Part', u'Chapter', u'Paragraph'): [[u'Part', u'Chapter', u'Paragraph'], ["חלק", "פרק", "פסקה"]],
    (u'Mitzvah', u'Paragraph'): [[u'Mitzvah', u'Paragraph'], ["מצוה", "פסקה"]],
    (u'Volume ', u'Chapter', u'Paragraph'): [[u'Volume', u'Chapter', u'Paragraph'], ["כרך", "פרק", "פסקה"]],
    (u'Story', u'Paragraph'): [[u'Story', u'Paragraph'], ["סיפור", "פסקה"]],
    (u'Parshah', u'Siman'): [[u'Parsha', u'Siman'], ["פרשה", "סימן"]],
    (u'Subject', u'Page', u''): [[u'Parsha', u'Page', u''], ["פרשה", "", "", ]],
    (u'Parshah', u'Siman Katan'): [[u'Parsha', u'Siman Katan'], ["פרשה", "", ]],
    (u'Shar', u'Chapter', u'Paragraph'): [[u'Gate', u'Chapter', u'Paragraph'], ["שער", "פרק", "פסקה"]],
    (u'Perek', u'Seif', u'Paragraph'): [[u'Chapter', u'Section', u'Paragraph'], ["פרק", "סעיף", "פסקה"]],
    (u"Sha'ar Ha'Gemul",): [[u"Paragraph"], ["פסקה"]],
    (u'Chapter',): [[u'Chapter'], ["פרק"]],
    (u'Chapter', u'Paragraph', u'Footnote'): [[u'Chapter', u'Paragraph', u'Footnote'], ["פרק", "פסקה", "הערת שוליים"]],
    (u'Teshuva', u'Paragraph'): [[u'Response', u'Paragraph'], ["תשובה", "פסקה"]],
    (u'Teshuva', u'Part'): [[u'Response', u'Part'], ["תשובה", "חלק"]],
    (u'Question', u'Paragraph'): [[u'Question', u'Paragraph'], ["שאלה", "פסקה"]],
    (u'Teshuva', u'Paragraph', u'Comment'): [[u'Response', u'Paragraph', u'Comment'], ["תשובה", "פסקה", "פירוש"]],
    (u'Perek', u'Verse'): [[u'Chapter', u'Verse'], ["פרק", "פסוק"]],
    (u'Verse',): [[u'Verse'], ["פסוק"]],
    (u'Chapter', u'Footnote'): [[u'Chapter', u'Footnote'], ["פרק", "הערת שוליים"]],
    (u'Comment',): [[u'Comment'], ["פירוש"]],
    (u'Comment', u'Paragraph'): [[u'Comment', u'Paragraph'], ["פירוש", "פסקה"]],
    (u'Chapter', u'Mishna', u'Paragraph'): [[u'Chapter', u'Mishna', u'Paragraph'], ["פרק", "משנה", "פסקה"]],
    (u'Segment',): [[u'Paragraph'], ["פסקה"]],
    (u'Halacha', u'siman'): [[u'Halacha', u'Siman'], ["הלכה", ""]],
    (u'Seif', u''): [[u'Seif', u''], ["סעיף", ""]],
    (u'Perek', u'Halacha', u'siman'): [[u'Chapter', u'Halacha', u'Siman'], ["פרק", "הלכה", ""]],

}

flat_sections = ["Chapter", "Gate", "Page", "Siman", "Parsha", "Day", "Drush", "Letter", "Essay", "Kovetz",
                 "Mitzvah", "Story", "Response", "Question"]
single_sections = ["Paragraph", "Halacha", "Remez", "Commandment", "Seif", "Section", "Line", "Verse", "Comment"]
level_sections = ["Volume", "Part", "Book", "Heichal"]

known_complex = ["Tafsir Rasag"]


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
        self.skip_title = "Shney Luchot HaBrit"
        self.section_types = []

    def get_section_type(self, sections):
        correct_sections = known_sections[tuple(sections)]
        if correct_sections not in self.section_types:
            self.section_types.append(correct_sections)
        return correct_sections, self.section_types.index(correct_sections)

    def walk_on_toc(self, toc_file_name="toc.xml"):
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
        self.toc_file = open(self.json_dir + '/' + toc_file_name, 'w+')
        self.toc_file.write('<?xml version="1.0" ?>\n<index name="onyourway">\n')
        self.walk_on_items(self.toc)
        self.toc_file.write('</index>')

    def handle_complex(self, schema, langs, level, names):
        print_node = 0
        if len(names['en']) > 1 or names['en'][0] != self.last_category:
            print_node = 1
            # self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
            #                                                        ', '.join([x.encode('utf-8').replace('"', "''") for x in
            #                                                                   names['he']]),
            #                                                        ', '.join(names['en'])))
            self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
                                                                   names['he'][-1].encode('utf-8').replace('"', "''"),
                                                                   names['en'][-1]))

        for node in schema['nodes']:
            node_short_names = dict(en=node['title'], he=node['heTitle'])
            node_long_names = dict(he=names['he'][:], en=names['en'][:])
            node_long_names['he'].append(node['heTitle'])
            node_long_names['en'].append(node['title'])
            node_langs = {}
            for lang in langs:
                try:
                    node_langs[lang] = langs[lang][node['title']]
                except KeyError:
                    logger.error("title: {}, missing complex key: {}".format(node_long_names, node['title']))
                    continue
            if 'nodes' in node:
                self.handle_complex(node, node_langs, level+print_node, node_long_names)
            else:
                self.handle_item(node_langs, node_short_names, node_long_names,
                                 dict(he=node['heSectionNames'],
                                      en=node['sectionNames']), level+print_node)
        if print_node:
            self.toc_file.write('{}</node>\n'.format(' ' * 4 * level))

    def handle_item(self, langs, short_titles, long_titles, sections, level):
        length = 0
        is_level = 0
        lang_type = 'both'
        if 'en' not in langs:
            lang_type = 'he'
        elif 'he' not in langs:
            lang_type = 'en'
        if sections['en'] in [[u'Line', u''], [u'Piyyut', u'Verse'], [u'Part', u'Line']]:
            for lang in langs:
                langs[lang] = langs[lang][0]
                sections['en'] = [u'Line']
        if sections['en'] in [[u'Seif', u'Siman']]:
            sections['en'] = [u'Seif', '']
        if tuple(sections['en']) not in known_sections:
            print tuple(sections['en']), ": [", sections['en'],
            print ', [',
            for k in sections['he']:
                print unicode('"' + k + '",').encode('utf-8'),
            print ']],'

            raise KeyError('title:{} unknown section: {} '.format(long_titles['en'], sections['en']))

        correct_sections, section_index = self.get_section_type(sections['en'])
        # if hierarchy not set right
        if correct_sections[0] in [[u'Line', u'']]:
            for lang in langs:
                langs[lang] = langs[lang][0]
            correct_sections = [[u'Line'], ["שורה"]]
        if correct_sections[0][0] in level_sections:
            is_level = 2
            for lang in langs:
                for volume, volume_data in enumerate(langs[lang]):
                    length = max(length, volume + 1)
                    for chap, data in enumerate(volume_data):
                        json.dump(data, open("{}/{}.{}.{}.{}.json".format(self.json_dir, self.counter,
                                                                          volume, chap, lang), 'w+'))

        elif correct_sections[0][0] in flat_sections:
            is_level = 1
            for lang in langs:
                for chap, data in enumerate(langs[lang]):
                    length = max(length, chap + 1)
                    json.dump(data, open("{}/{}.{}.{}.json".format(self.json_dir, self.counter,
                                                                   chap, lang), 'w+'))
        elif correct_sections[0][0] in single_sections:
            is_level = 0
            for lang in langs:
                json.dump(langs[lang], open("{}/{}.{}.json".format(self.json_dir, self.counter,
                                                                   lang), 'w+'))
        else:
            raise KeyError('title:{} unknown section layout: {}'.format(short_titles['en'], correct_sections))

        self.toc_file.write('{}<node n="{}" en="{}" i="{}" chaps="{}" lang="{}" level="{}"/>\n'.
                            format(' ' * 4 * level, short_titles['he'].
                                   encode('utf-8').replace('"', "''"),
                                   short_titles['en'],
                                   self.counter,
                                   length,
                                   lang_type,
                                   is_level))

        self.toc_data['hebrew_long_index'][self.counter] = ', '.join([x.encode('utf-8').replace('"', "''") for x in long_titles['he']])
        self.toc_data['hebrew_short_index'][self.counter] = short_titles['he'].encode('utf-8').replace('"', "''")
        self.toc_data['books_index'][self.counter] = [', '.join(long_titles['en']), is_level]
        self.toc_data['books_short_index'][self.counter] = [short_titles['en'], is_level]
        self.toc_data['reverse_index'][', '.join(long_titles['en'])] = self.counter
        self.toc_data['book_section_type'][self.counter] = section_index
        self.counter += 1

    def walk_on_items(self, items, level=0, path='/json'):
        for item in items:
            if "category" in item:
                self.last_category = item[u'category']
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
                if not os.path.isfile(src_dir+en_file) and not os.path.isfile(src_dir+he_file):
                    logger.error("missing lang, path: {}".format(src_dir))
                    continue
                langs = dict()
                schema = None
                try:
                    schema = json.load(open("{}/schemas/{}.json".format(self.export_path, title.replace(' ', '_'))))
                except Exception:
                    logger.error("empty schema: {}/schemas/{}.json".format(self.export_path, title.replace(' ', '_')))
                is_complex = False
                if os.path.isfile(src_dir + he_file):
                    he = json.load(open(src_dir + he_file))
                    langs['he'] = he["text"]
                    if "schema" in he:
                        is_complex = True
                if os.path.isfile(src_dir + en_file):
                    en = json.load(open(src_dir + en_file))
                    langs['en'] = en["text"]
                    if "schema" in en:
                        is_complex = True
                if not is_complex:
                    self.handle_item(langs, dict(en=title, he=he_title), dict(en=[title], he=[he_title]),
                                     dict(en=schema["schema"]["sectionNames"], he=schema["schema"]["heSectionNames"]),
                                     level)
                    # if len(correct_sections[0][is_level:]) > 1:
                    #     logger.error("title: {}, level in file: {}, level: {}, sectoins: {}".format(title, len(correct_sections[0][is_level:]),
                    #                                                                                 is_level, correct_sections[0]))

                else:
                    # complex text
                    # if title not in known_complex:
                    #     logger.warning("complex: {}".format(title))
                    #     raise
                    names = dict(he=[schema['heTitle']], en=[schema['title']])
                    self.handle_complex(schema=schema['schema'], langs=langs, level=level, names=names)


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
                if title in add_base_title_from_on:
                    item["base_text_mapping"] = "one_to_one"
                    item["base_text_titles"] = [title.split('on ')[1]]
                if "Minchat Shai" in title and title != "Minchat Shai on Torah":
                    item["base_text_mapping"] = "one_to_one"
                if "Ba'er Hetev on Shulchan Arukh" in title or "Beur HaGra on Shulchan Arukh" in title:
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
                    try:
                        orig_id = self.toc_data["reverse_index"][item["base_text_titles"][0].replace('_', ' ')]
                        comment_id = self.toc_data["reverse_index"][title]
                    except Exception:
                        logger.error("complex not ready yet (?): {}".format(title))
                        continue
                    self.toc_data["commentary"][orig_id].append((comment_id, 0))
                elif item.get("base_text_titles"):
                    if title in not_direct_commentary or item["collectiveTitle"] in collective_not_direct_commentary:
                        for i in item["base_text_titles"]:
                            orig_id = self.toc_data["reverse_index"][i]
                            comment_id = self.toc_data["reverse_index"][title]
                            self.toc_data["commentary"][orig_id].append((comment_id, 2))
                    elif title in complex_commentary_empty_string or "Tosafot Yom Tov on" in title:
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
                    if title in ["Darchei HaTalmud", "Introductions to the Babylonian Talmud"]:
                        continue
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
