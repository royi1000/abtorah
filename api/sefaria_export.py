# coding=utf-8

import os
import shutil
import logging
import json
import argparse
from collections import defaultdict
from colorlog import ColoredFormatter
import csv
import glob
import pickle

logging.basicConfig()
logger = logging.Logger(__name__, logging.INFO)

en_file = '/English/merged.json'
he_file = '/Hebrew/merged.json'

tanach_list = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "I Samuel", "II Samuel",
               "I Kings", "II Kings", "Jeremiah", "Ezekiel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
               "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Psalms", "Proverbs", "Job",
               "Song of Songs", "Ruth", "Lamentations", "Ecclesiastes", "Esther", "Daniel", "Ezra", "Nehemiah",
               "I Chronicles", "II Chronicles",
                ]
torah_list = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

heb_mapping = {
    "Genesis": "Bereshit",
    "Exodus": "Shemot",
    "Leviticus": "Vayikra",
    "Numbers": "Bamidbar",
    "Deuteronomy": "Devarim"
}

heb_mapping_inv = {v: k for k, v in heb_mapping.iteritems()}

# one to one dict +key comment
complex_commentary = ["Alshich on Torah", "Abarbanel on Torah", "Tur HaAroch", "Avi Ezer", "Bekhor Shor", "Chizkuni",
                      "Minchat Shai on Torah", "Rabbeinu Bahya", "Siftei Hakhamim", "Marganita Tava al Sefer Hamitzvot",
                      "Megilat Esther al Sefer Hamitzvot", "Kinaat Sofrim al Sefer Hamitzvot", "Raavad on Sefer Yetzirah",
                      "Marpeh la'Nefesh", "Pat Lechem", "Tov haLevanon", "Mizrachi",

                      ]


not_direct_commentary = ["Akeidat Yitzchak", "Meshech Hochma", "Penei David", "Shney Luchot HaBrit",
                         "Rambam Introduction to Masechet Horayot", "Divrey Chamudot",
                         "Darchei HaTalmud", 'Mordechai on Bava Batra',
                         'Brit Moshe', 'Introductions to the Babylonian Talmud', 'Divrey Chamudot', 'Maadaney Yom Tov',
                         "Rosh", "Yad Ramah"]

# not_direct_commentary_title = ['Beur HaGra on Shulchan Arukh, Choshen Mishpat',
#                            'Netivot HaMishpat, Beurim on Shulchan Arukh, Choshen Mishpat',
#                            'Netivot HaMishpat, Hidushim on Shulchan Arukh, Choshen Mishpat'
# ]

collective_not_direct_commentary = ["Rif", "Yachin", "Boaz", "Divrey Chamudot", "Maadaney Yom Tov",
                                    "Pilpula Charifta", 'Rosh', "Korban Netanel", "Tiferet Shmuel", "Yad Ramah"]
perek_commentarry = []
perek_commentarry_title = ['Chiddushei Ramban']

perek_commentarry_collective = ["Rashba", "Chidushei Agadot", "Chidushei Halachot", "Chokhmat Shlomo", "Maharam",
                                "Maharam Shif", 'Ritva', "Tosafot Rid", "Melechet Shlomo", "Zeroa Yamin", "Ba'er Hetev",
                                "Shita Mekubetzet"]

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
                                   "Beur HaGra on Shulchan Arukh, Choshen Mishpat", "Footnotes on Mekhilta DeRabbi Shimon Bar Yochai"
                                   "Netivot HaMishpat, Hidushim on Shulchan Arukh, Choshen Mishpat",
                                   "Pithei Teshuva on Shulchan Arukh, Choshen Mishpat",
                                   "Siftei Kohen on Shulchan Arukh, Choshen Mishpat",
                                   'Netivot HaMishpat, Hidushim on Shulchan Arukh, Choshen Mishpat']

base_title_complex_string = ["Mekhilta DeRabbi Shimon Bar Yochai", "Tractate Derekh Eretz Zuta", 'Seder Olam Rabbah']
add_base_title_from_on = ["Shita Mekubetzet on Berakhot", 'Shita Mekubetzet on Beitzah',
                          "Be'er HaGolah on Shulchan Arukh, Choshen Mishpat", "Ketzot HaChoshen on Shulchan Arukh, Choshen Mishpat",
                          "Me'irat Einayim on Shulchan Arukh, Choshen Mishpat", "Netivot HaMishpat, Beurim on Shulchan Arukh, Choshen Mishpat",
                          "Netivot HaMishpat, Hidushim on Shulchan Arukh, Choshen Mishpat", "Pithei Teshuva on Shulchan Arukh, Choshen Mishpat",
                          "Siftei Kohen on Shulchan Arukh, Choshen Mishpat"]

chap_sect = dict(he=u'פרקים', en='chapters')
siman_sect = dict(he=u'סימנים', en='Simanim')
halach_sect = dict(he=u'הלכות', en='Halachos')
allowed_empty_titles_chaps = {u'Divrey Chamudot on ': siman_sect, u'Maadaney Yom Tov on ': siman_sect,
                              u'Rosh on ': siman_sect}

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
    (u'Chapter', u'Midrash'): [[u'Chapter', u'Midrash'], ["פרק", "מדרש"]],
    (u'Paragraph', u'Comment'): [[u'Paragraph', u'Comment'], ["פסקה", "פירוש"]],
    (u'Halakhah',): [[u'Halacha'], ["הלכה"]],
    (u'Halakhah', u'Comment'): [[u'Halacha', u'Comment'], ["הלכה", "פירוש"]],
    (u'Article', u'Paragraph'): [[u'Seif', u'Paragraph'], ["סעיף", "פסקה"]],
    (u'Seif', u'Paragraph'): [[u'Siman', u'Paragraph'], ["סימן", "פסקה"]],
    (u'Mitzvah', u'Siman'): [[u'Mitzvah', u'Seif'], ["מצוה", "סימן"]],
    (u'Mitzvah', u'Seif', u'Paragraph'): [[u'Mitzvah', u'Seif', u'Paragraph'], ["מצוה", "סעיף", "פסקה"]],
    (u'Shoresh', u'Seif'): [[u'Shoresh', u'Seif'], ["שורש", "סעיף"]],
    (u'Seif',): [[u'Seif'], ["סעיף"]],
    (u'Mitzvah', u'Seif'): [[u'Mitzvah', u'Seif'], ["מצוה", "סעיף"]],
    (u'Negative Mitzvah', u'Paragraph'): [[u'Mitzvah', u'Paragraph'], ["מצוה", "פסקה"]],
    (u'Positive Mitzvah', u'Paragraph'): [[u'Mitzvah', u'Paragraph'], ["מצוה", "פסקה"]],
    (u'Siman', u'Seif Katan', u'Paragraph'): [[u'Siman', u'Seif Katan', u'Paragraph'], ["סימן", "סעיף קטן", "פסקה"]],
    (u'Siman', u'Seif', u'Seif Katan'): [[u'Siman', u'Seif', u'Seif Katan'], ["סימן", "סעיף", "סעיף קטן"]],
    (u'Article', u'Paragraph', u'Comment'): [[u'Seif', u'Paragraph', u'Comment'], ["סעיף", "פסקה", "פירוש"]],
    (u'Shorash', u'Comment'): [[u'Shoresh', u'Comment'], ["שורש", "פירוש"]],
    (u'Shoresh', u'Comment'): [[u'Shoresh', u'Comment'], ["שורש", "פירוש"]],
    (u'Section', u'Mitzvah'): [[u'Section', u'Mitzvah'], ["חלק", "מצוה"]],
    (u'Mitzvah', u'Comment'): [[u'Mitzvah', u'Comment'], ["מצוה", "פירוש"]],
    (u'Section', u'Comment'): [[u'Section', u'Comment'], ["חלק", "פירוש"]],
    (u'Shoresh', u'Siman', u'Parshanut'): [[u'Shoresh', u'Seif', u'Comment'], ["שורש", "סעיף", "פירוש"]],
    (u'Mitzvah', u'Siman', u'Parshanut'): [[u'Mitzvah', u'Seif', u'Comment'], ["מצוה", "סעיף", "פירוש"]],
    (u'Shoresh', u'Siman'): [[u'Shoresh', u'Siman'], ["שורש", "סימן"]],
    (u'Mitzvah', u'Comment', u'Paragraph'):[[u'Mitzvah', u'Comment', u'Paragraph'] , ["מצוה", "פירוש", "פסקה"]],
    (u'Gate', u'Chapter'): [[u'Part', u'Chapter'], ["שער", "פרק"]],
    (u'Gate', u'Chapter', u'Paragraph'): [[u'Part', u'Chapter', u'Paragraph'], ["שער", "פרק", "פסקה"]],
    (u'Nahar', u'Paragraph'): [[u'River', u'Paragraph'], ["נהר", "פסקה"]],
    (u'Shoket', u'Paragraph'): [[u'Shoket', u'Paragraph'], ["שוקת", "פסקה"]],
    (u'Shaar', u'Paragraph'): [[u'Gate', u'Paragraph'], ["שער", "פסקה", ]],
    (u'Chapter', u'Paragraph', u'Segment'): [[u'Chapter', u'Paragraph', u'Segment'], ["פרק", "פסקה", ""]],
    (u'Path',): [[u'Path'], ["נתיב"]],
    (u'Subsection',): [[u'Seif'], ["סעיף"]],
    (u'Subsection', u'Comment'): [[u'Seif', u'Comment'], ["סעיף", "פירוש", ]],
    (u'Chapter', u'Mishnah', u'Paragraph'): [[u'Chapter', u'Mishna', u'Paragraph'], ["פרק", "משנה", "פסקה"]],
    (u'Treatise', u'Paragraph'): [[u'Treatise', u'Paragraph'], ["מאמר", "פסקה"]],
    (u"'Comment'", u"'Paragraph'"): [[u"Comment", u"Paragraph"], ["פירוש", "פסקה"]],
    (u"'Epistle'", u"'Paragraph'"): [[u"Epistle", u"Paragraph"], ["אגרת", "פסקה"]],
    (u'Torah', u'Section'): [[u'Torah', u'Section'], ["תורה", "חלק"]],
    (u'Manuscript', u'Paragraph'): [[u'Manuscript', u'Paragraph'], ["כתב יד", "פסקה"]],
    (u'Chapter', u'Section', u'Paragraph'): [[u'Chapter', u'Section', u'Paragraph'], ["פרק", "חלק", "פסקה"]],
    (u'Mishnah', u'Paragraph'): [[u'Mishna', u'Paragraph'], ["משנה", "פסקה"]],
    (u'Word', u'Paragraph') : [ [u'Word', u'Paragraph'] , [ "מלה", "פסקה", ]],
    (u'Principle', u'Paragraph'): [[u'Principle', u'Paragraph'], ["עקרון", "פסקה"]],
    (u'Chapter', u'S'): [[u'Chapter', u'Paragraph'], ["פרק", "פסקה"]],
}

flat_sections = ["Chapter", "Gate", "Page", "Siman", "Parsha", "Day", "Drush", "Letter", "Essay", "Kovetz",
                 "Mitzvah", "Story", "Response", "Question", "Shoresh", "Shoket", "River", "Path", "Treatise",
                 "Epistle", "Torah", "Manuscript", "Word", "Principle"]
single_sections = ["Paragraph", "Halacha", "Remez", "Commandment", "Seif", "Section", "Line", "Verse", "Comment", "Mishna"]
level_sections = ["Volume", "Part", "Book", "Heichal"]


# comment types: 0 - one on one, 1 - one on one dict, , 2 - one on one dict (empty string key),
# 3 - commentary to chapter level, 4 - not direct
COM_ONE_ON_ONE = 0
COM_ONE_ON_ONE_DICT = 1
COM_ONE_ON_ONE_DICT_EMPTY = 2
COM_CHAP_LEVEL = 3
COM_NOT_DIRECT = 4


def sef_logger():
    color_formatter = ColoredFormatter("%(log_color)s %(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s")
    sh = logging.StreamHandler()
    sh.setFormatter(color_formatter)
    logger.addHandler(sh)
    logger.info("Logger Initialized")


def txt_in_partial_list(title, partial_title_list):
    for z in partial_title_list:
        if z in title:
            return z
    return False


class TOC(object):
    DEFAULT_PATH = os.path.expanduser('~/Sefaria-Export')

    def __init__(self, export_path, dest_path):
        self.export_path = export_path
        self.toc = json.load(open(self.export_path+'/table_of_contents.json'))
        self.toc_data = defaultdict(dict)
        self.toc_data['section_types'] = []
        self.comment_map = defaultdict(list)
        self.counter = 1
        self.json_dir = dest_path
        self.toc_data["commentary"] = defaultdict(defaultdict)
        # for fast debug
        self.skip = False
        self.skip_title = "Shney Luchot HaBrit"
        self.section_types = []
        self.complex = []
        self.refs = defaultdict(dict)

    def get_section_type(self, sections):
        correct_sections = known_sections[tuple(sections)]
        if correct_sections not in self.toc_data['section_types']:
            self.toc_data['section_types'].append(correct_sections)
        return correct_sections, self.toc_data['section_types'].index(correct_sections)

    def get_sction_from_index(self, index):
        return self.toc_data['section_types'][index]

    def walk_on_toc(self, toc_file_name="toc.xml"):
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
        self.toc_file = open(self.json_dir + '/' + toc_file_name, 'w+')
        self.toc_file.write('<?xml version="1.0" ?>\n<index name="onyourway">\n')
        self.walk_on_items(self.toc)
        self.toc_file.write('</index>')
        self.toc_file.close()
        self.toc_file = None

    def handle_complex(self, schema, langs, level, names, item):
        print_node = 0
        if len(names['en']) > 1 or names['en'][0] != self.last_category:
            print_node = 1
            # self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
            #                                                        ', '.join([x.encode('utf-8').replace('"', "''") for x in
            #                                                                   names['he']]),
            #                                                        ', '.join(names['en'])))
            self.toc_file.write('{}<node n="{}" en="{}">\n'.format(' ' * 4 * level,
                                                                   names['he'][-1].encode('utf-8').replace('"', "''"),
                                                                   names['en'][-1].replace('"', "''").replace('&', " and ")))

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
                self.handle_complex(node, node_langs, level+print_node, node_long_names, item)
            else:
                self.handle_item(node_langs, node_short_names, node_long_names,
                                 dict(he=node['heSectionNames'],
                                      en=node['sectionNames']), level+print_node, item)
        if print_node:
            self.toc_file.write('{}</node>\n'.format(' ' * 4 * level))

    def verify_sections(self, sections, orig_id):
        orig_list = self.get_sction_from_index(self.toc_data['book_section_type'][orig_id])[0]
        if orig_list != sections[0][:len(orig_list)]:
            logger.error("verify section failed orig: {} comment: {}".format(orig_list, sections[0]))
            raise ValueError("verify section failed orig: {} comment: {}".format(orig_list, sections[0]))

    def handle_item(self, langs, short_titles, long_titles, sections, level, item=None):
        length = 0
        is_level = 0
        lang_type = 'both'
        if [u'Commentary on Sefer Hamitzvot of Rasag', u'Negative Commandments'] == long_titles['en']:
            pass
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

        if short_titles['en'] == "":
            if correct_sections[0][0] == 'Chapter':
                short_titles = dict(he=u'פרקים', en='chapters')
            elif correct_sections[0][0] == 'Paragraph':
                short_titles = dict(he=u'תוכן', en='text')
            elif correct_sections[0][0] == 'Siman':
                short_titles = siman_sect
            elif correct_sections[0][0] == 'Seif':
                short_titles = dict(he=u'סעיפים', en='Seif\'s')
            elif correct_sections[0][0] == 'Mitzvah':
                short_titles = dict(he=u'מצוות', en='Commandments')
            elif correct_sections[0][0] == 'Comment':
                short_titles = dict(he=u'הערות', en='Comment')
            elif correct_sections[0][0] in ['Part', 'Gate']:
                short_titles = dict(he=u'שערים', en='Gates')
            elif correct_sections[0][0] == 'Path':
                short_titles = dict(he=u'דרכים', en='Paths')
            elif correct_sections[0][0] == 'Treatise':
                short_titles = dict(he=u'מאמרים', en=u'Treatise')
            elif correct_sections[0][0] == u'Epistle':
                short_titles = dict(he=u'אגרות', en=u'Epistles')
            elif correct_sections[0][0] == u'Torah':
                short_titles = chap_sect
            elif correct_sections[0][0] == 'Word':
                short_titles = dict(he=u'מילים', en=u'Words')
            elif correct_sections[0][0] == 'Principle':
                short_titles = dict(he=u'עקרונות', en=u'Principles')

            else:
                new_scet = txt_in_partial_list(long_titles['en'][0], allowed_empty_titles_chaps.keys())
                if new_scet:
                    short_titles = allowed_empty_titles_chaps[new_scet]
                else:
                    raise ValueError("long titles: {}".format(long_titles['en'][:-1]))

        self.toc_file.write('{}<node n="{}" en="{}" i="{}" chaps="{}" lang="{}" level="{}"/>\n'.
                            format(' ' * 4 * level, short_titles['he'].
                                   encode('utf-8').replace('"', "''"),
                                   short_titles['en'].replace('&', " and ").replace('"', "''"),
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
        if item:
            if long_titles['en'][0] == u'Lev Sameach':
                short_titles['en'] = short_titles['en'].replace("Positive Commandments", "Mitzvot Ase")
                short_titles['en'] = short_titles['en'].replace("Negative Commandments", "Mitzvot Lo Taase")
                long_titles['en'][-1] = short_titles['en']

            title = short_titles['en']
            if long_titles['en'][0] in not_direct_commentary or item['collectiveTitle'] in not_direct_commentary:
                self.counter += 1
                return
            full_name = ', '.join(long_titles['en'])
            if long_titles['en'][0] in ["Rabbeinu Bahya"]:
                try:
                    long_titles['en'][1] = heb_mapping_inv[long_titles['en'][1]]
                except KeyError:
                    pass
            if "base_text_titles" in item and long_titles['en'][1] in item["base_text_titles"]:
                comment_type = COM_ONE_ON_ONE_DICT
                i = long_titles['en'][1]
                orig_id = self.toc_data["reverse_index"][i]
                if title in ["Siftei Hakhamim"]:
                    i = i.split("on ")[-1]
                self.toc_data["commentary"][orig_id][self.counter] = comment_type
            elif long_titles['en'][0] in ['Siftei Hakhamim']:
                comment_type = COM_ONE_ON_ONE_DICT
                orig = long_titles['en'][1]
                orig_id = self.toc_data["reverse_index"][orig]
                self.verify_sections(correct_sections, orig_id)
                self.toc_data["commentary"][orig_id][self.counter] = comment_type
            elif "base_text_titles" not in item and long_titles['en'][1] in self.toc_data["reverse_index"]:
                comment_type = COM_ONE_ON_ONE_DICT
                logger.debug("guessing base: {}, title: {}".format(long_titles['en'][1], full_name))
                orig = long_titles['en'][1]
                orig_id = self.toc_data["reverse_index"][orig]
                self.verify_sections(correct_sections, orig_id)
                self.toc_data["commentary"][orig_id][self.counter] = comment_type
            elif long_titles['en'][1] == "":
                comment_type = COM_ONE_ON_ONE_DICT_EMPTY
                if "base_text_titles" in item and len(item["base_text_titles"]) == 1 and item["base_text_titles"][0] in full_name:
                    orig = item["base_text_titles"][0]
                elif ' on ' in long_titles['en'][0]:
                    orig = long_titles['en'][0].split(' on ')[-1]
                    if "base_text_titles" in item and orig not in item["base_text_titles"]:
                        logger.warning("comment: {} orig: {} not in item base text".format(full_name, orig))
                        raise
                elif full_name == u'Magen Avot, ':
                    orig = item["base_text_titles"][0]
                else:
                    raise
                if orig in self.complex:
                    orig += ', '
                orig_id = self.toc_data["reverse_index"][orig]
                if full_name not in ["Raavad on Sefer Yetzirah, "]:
                    self.verify_sections(correct_sections, orig_id)
                    self.toc_data["commentary"][orig_id][self.counter] = comment_type

            elif (txt_in_partial_list(long_titles['en'][0],
                                      [u'Tafsir Rasag', u'Ibn Ezra', u'Rabbeinu Bahya', u'Ralbag',
                                       u'Divrey Chamudot on Menachot', u'Maadaney Yom Tov on ',
                                       u'Tur HaAroch',u'Magen Avot', u'Tosafot Yom Tov on ',
                                       u'Vilna Gaon on Seder Olam Rabbah',u'Yaakov Emden on ',
                                       u'Footnotes on Mekhilta DeRabbi Shimon Bar Yochai',
                                       u'Marganita Tava al Sefer Hamitzvot',
                                       u'Megilat Esther al Sefer Hamitzvot',
                                       u'Commentary on Sefer Hamitzvot of Rasag'
                                       ]) and
                    txt_in_partial_list(long_titles['en'][1], [u'Introduction', u'Prelude', u'Additions',u'Title Page',
                                                               u'Foreword',
                                                               u'Translators Foreword', u'Benefits', u'Hilchot'])) or \
                full_name in [u'Beur HaGra on Shulchan Arukh, Choshen Mishpat, Dinei Migo',
                              u'Netivot HaMishpat, Beurim on Shulchan Arukh, Choshen Mishpat, Klalei Tefisa',
                              u'Netivot HaMishpat, Hidushim on Shulchan Arukh, Choshen Mishpat, Klalei Tefisa',
                              u'Pithei Teshuva on Shulchan Arukh, Choshen Mishpat, Klalei Tefisa',
                              u'Pithei Teshuva on Shulchan Arukh, Choshen Mishpat, Dinei Migo',
                              u'Siftei Kohen on Shulchan Arukh, Choshen Mishpat, Dinei Migo',
                              u"Marpeh la'Nefesh, Introduction to Commentary",
                              u'Pat Lechem, Introduction to Commentary',
                              u'Tov haLevanon, Introduction of the Author',

                              ] or u'Raavad on Sefer Yetzirah, Introduction' in full_name:
                logger.debug("complex comment, skip: {}".format(full_name))
            elif "base_text_titles" in item and len(item["base_text_titles"]) == 1 and item["base_text_titles"][0] in full_name or \
                            'al Sefer Hamitzvot' in long_titles['en'][0] or long_titles['en'][0] in [u'Lev Sameach',
                                                u"Marpeh la'Nefesh", u'Pat Lechem', u'Tov haLevanon']:
                ignore = False
                if txt_in_partial_list(long_titles['en'][0], ['al Sefer Hamitzvot', 'Lev Sameach']) and \
                        'Marganita Tava al Sefer Hamitzvot' not in long_titles['en'][0]:
                    item["base_text_titles"] = ['Hasagot HaRamban al Sefer HaMitzvot']
                    ignore = True
                if long_titles['en'][0] == u'Commentary on Sefer Hamitzvot of Rasag':
                    ignore = True
                comment_type = COM_ONE_ON_ONE_DICT
                if long_titles['en'][0] in [u"Marpeh la'Nefesh", u'Pat Lechem', u'Tov haLevanon']:
                    ignore = True
                    comment_type = COM_CHAP_LEVEL
                orig = ', '.join(item["base_text_titles"] + long_titles['en'][1:])
                logger.debug("multi level complex, orig: {} comment: {}".format(orig, full_name))
                if orig + ', ' in self.toc_data["reverse_index"]:
                    orig += ', '
                if not ignore:
                    orig_id = self.toc_data["reverse_index"][orig]
                    self.verify_sections(correct_sections, orig_id)
                    self.toc_data["commentary"][orig_id][self.counter] = comment_type
            else:
                raise

        self.counter += 1

    def walk_on_items(self, items, level=0, path='/json'):
        for item in items:
            if "category" in item:
                if not level:
                    logger.info(item[u'category'])
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
                try:
                    schema = json.load(open("{}/schemas/{}.json".format(self.export_path, title.replace(' ', '_'))))
                except Exception:
                    logger.error("empty schema: {}/schemas/{}.json, complex: {}".format(self.export_path, title.replace(' ', '_'), is_complex))
                    if is_complex:
                        continue
                if not is_complex:
                    title = title.replace("Mitzvot Ase", "Positive Commandments")
                    title = title.replace("Mitzvot Lo Taase", "Negative Commandments")
                    self.handle_item(langs, dict(en=title, he=he_title), dict(en=[title], he=[he_title]),
                                     dict(en=schema["schema"]["sectionNames"], he=schema["schema"]["heSectionNames"]),
                                     level)
                else:
                    c = None
                    if item.get("dependence") and is_complex:
                        c = item
                    # complex text
                    names = dict(he=[schema['heTitle']], en=[schema['title']])
                    self.complex.append(title)
                    self.handle_complex(schema=schema['schema'], langs=langs, level=level, names=names, item=c)

    def walk_on_commentary(self, items=None):
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
                if title in self.complex:
                    continue
                if title == 'Commentary on Sefer Hamitzvot of Rasag, Negative Commandments':
                    pass
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
                            comment_type = COM_ONE_ON_ONE_DICT
                            for i in item["base_text_titles"]:
                                orig_id = self.toc_data["reverse_index"][i]
                                if title in ["Rabbeinu Bahya"]:
                                    i = heb_mapping[i]
                                if title in ["Siftei Hakhamim"]:
                                    i = i.split("on ")[-1]
                                comment_id = self.toc_data["reverse_index"]["{}, {}".format(title, i)]
                                self.toc_data["commentary"][orig_id][comment_id] = comment_type
                            continue
                        else:
                            logger.error("invalid len base_text_titles: {} in: {}, mapping: {}".format(len(item["base_text_titles"]),
                                                                                               title,item["base_text_mapping"]))
                    try:
                        base = item["base_text_titles"][0].replace('_', ' ')
                        t = title
                        if base in base_title_complex_string:
                            base += ", "
                            t += ", "
                        elif t in complex_commentary_empty_string:
                            t += ", "
                        orig_id = self.toc_data["reverse_index"][base]
                        comment_id = self.toc_data["reverse_index"][t]
                    except Exception:
                        logger.error("complex not ready yet (?): {}".format(title))
                        continue
                        if title in ["Meir Ayin on Seder Olam Rabbah"] or \
                                     'Mishneh Torah' in title:
                            continue
                        else:
                            raise
                    if txt_in_partial_list(title, perek_commentarry_title) or ("collectiveTitle" in item and item["collectiveTitle"] in perek_commentarry_collective):
                        if comment_id == 2058:
                            pass
                        self.toc_data["commentary"][orig_id][comment_id] = COM_CHAP_LEVEL
                    else:
                        self.toc_data["commentary"][orig_id][comment_id] = COM_ONE_ON_ONE
                elif item.get("base_text_titles"):
                    if title in not_direct_commentary or item["collectiveTitle"] in collective_not_direct_commentary:
                        continue
                        # for i in item["base_text_titles"]:
                        #     orig_id = self.toc_data["reverse_index"][i]
                        #     comment_id = self.toc_data["reverse_index"][title]
                        #     self.toc_data["commentary"][orig_id].append((comment_id, COM_NOT_DIRECT))
                    elif title in complex_commentary_empty_string or "Tosafot Yom Tov on" in title:
                        base_item = item["base_text_titles"][0].replace('_', ' ')
                        if base_item in base_title_complex_string:
                            base_item += ', '
                        orig_id = self.toc_data["reverse_index"][base_item]
                        comment_id = self.toc_data["reverse_index"]["{}, ".format(title)]
                        self.toc_data["commentary"][orig_id][comment_id] = COM_ONE_ON_ONE_DICT_EMPTY
                    elif item['collectiveTitle']in perek_commentarry_collective or \
                            txt_in_partial_list(title, perek_commentarry_title):
                        orig_id = self.toc_data["reverse_index"][item["base_text_titles"][0].replace('_', ' ')]
                        comment_id = self.toc_data["reverse_index"][title]
                        self.toc_data["commentary"][orig_id][comment_id] = COM_CHAP_LEVEL
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

    def insert_ref(self, refa, refb):
        sections = self.get_sction_from_index(self.toc_data['book_section_type'][int(refa[0])])[0][:]
        ref = self.refs[refa[0]]
        if sections == [u'Line']:
            if len(refa[1:]) > 1:
                logger.debug(
                    "align line level, src: {} {}".format(self.toc_data["books_index"][int(refa[0])], refa))
                assert (refa[1] == '1')
                refa.pop(1)
        for r in refa[1:]:
            sections.pop(0)
            if r == '0':
                pass
            if r not in ref:
                if sections:
                    ref[r] = {}
                else:
                    ref[r] = []
                ref = ref[r]
        if type(ref) is list:
            ref.append(refb)
        else:
            logger.debug("comment in chap level, src: {} {}".format(self.toc_data["books_index"][int(refa[0])], refa))
            if "0" not in ref:
                ref["0"] = []
            ref["0"].append(refb)

    def compare_lists_start(self, list_a, list_b):
        for l in xrange(min(len(list_a), len(list_b))):
            if list_a[l] != list_b[l]:
                return False
        return True

    def get_refs(self):
        link_files = glob.glob("{}/links/links?.csv".format(self.export_path))
        link_count = 0
        direct_comment = {}
        chapter_direct_comment = {}
        valid_link_count = 0
        pairs = defaultdict(list)
        ignore_pairs = []
        for link_file in link_files:
            with open(link_file) as csv_file:
                csv_reader = csv.reader(csv_file)
                # first line
                csv_reader.next()
                for row in csv_reader:
                    if row == ['Commentary on Sefer Hamitzvot of Rasag, Negative Commandments 10', 'Sefer Hamitzvot of Rasag, Negative Commandments 10', 'commentary', 'Commentary on Sefer Hamitzvot of Rasag, Negative Commandments', 'Sefer Hamitzvot of Rasag, Negative Commandments', 'Halakhah', 'Halakhah']:
                        pass
                    link_count += 1
                    refs = row[:2]
                    ignore_list = ["JPS 1985 Footnotes", "Targum Neofiti"]
                    ignore = False
                    count = True
                    row[1] = row[1].replace('Ralbag on Iyov', 'Ralbag on Job')
                    for r in [row[3], row[4]]:
                        if txt_in_partial_list(r, ['Rif', "B'Mareh HaBazak", "Ba'er Hetev", "Ikar Tosafot Yom Tov on ", 'Mordechai on ', 'Rosh',
                                                   'Shita Mekubetzet on Bava Metzia', "Be'er Mayim Chaim", "Darchei Moshe", 'Bemidbar Rabbah',
                                                   'Abraham Cohen Footnotes to the English', 'Bereishit Rabbah', 'Brit Moshe, ', 'Commentary on Sefer Hamitzvot of Rasag',
                                                   'Daf Shevui to', 'Devarim Rabbah', 'Duties of the Heart', 'Eichah Rabbah',
                                                   'Footnotes to Teshuvot haRashba part ', 'Guide for the Perplexed', 'Gur Aryeh on ',
                                                    'Megilat Esther al Sefer Hamitzvot', 'Marganita Tava al Sefer', 'Avi Ezer',
                                                   'Ibn Ezra on', 'Kohelet Rabbah', 'Likutei Moharan', 'Mahberet Menachem',
                                                   'Malbim Beur Hamilot on Psalms', 'Mekhilta DeRabbi ', "Mekhilta d'Rabbi Yishmael",
                                                   'Meshech Hochma, ', 'Messilat Yesharim', 'Midrash Mishlei', 'Midrash Tanchuma',
                                                   'Midrash Tehillim', 'Minchat Chinukh', 'Yachin on ', 'Orchot Tzadikim',
                                                   ]):
                            count = False
                    if [row[5], row[6]] in [['Talmud', 'Tanakh'], ['Mishnah', 'Talmud'], ['Halakhah', 'Tanakh'], ['Philosophy', 'Tanakh'],
                                            ['Musar', 'Tanakh'], ['Musar', 'Mishnah'], ['Musar', 'Talmud'], ['Mishnah', 'Tanakh'], ['Midrash', 'Tanakh'],
                                            ['Mishnah', 'Philosophy'], ]:
                        count = False
                    elif ([row[3], row[4]] in [['Arakhin', 'Leviticus'], ['Aruch HaShulchan', 'Shabbat'],
                                               ['Avodah Zarah', 'Rosh on Avodah Zarah'], ['Bava Batra', 'Shulchan Arukh, Choshen Mishpat'],
                                               ['Bava Batra', 'Tur, Choshen Mishpat'], ['Bava Batra', 'Sefer Mitzvot Gadol, Positive Commandments'],
                                               ['Bava Batra', 'Rosh on Bava Batra'], ['Bava Batra', 'Mishneh Torah, Inheritances'],
                                               ['Bava Kamma', 'Exodus'], ['Bava Kamma', 'Leviticus'], ['Bava Kamma', 'Deuteronomy'],
                                               ['Bava Metzia', 'Deuteronomy'], ['Bava Metzia', 'Leviticus'], ['Berakhot', 'Deuteronomy'],
                                               ['Berakhot', 'Psalms'], ['Chizkuni, Exodus', 'Exodus'], ['Chizkuni, Genesis', 'Genesis'],
                                               ['Chullin', 'Leviticus'], ['Genesis', 'The Midrash of Philo'], ['Haamek Davar on Genesis', 'Harchev Davar on Genesis'],
                                               ['Maggid Mishneh on Mishneh Torah, Sabbath', 'Shabbat'], ['Metzudat Zion on Isaiah', 'Psalms'],
                                               ['Mishnah Berurah', 'Shulchan Arukh, Orach Chayim'],
                                               ['Mishneh Torah, Negative Mitzvot', 'Leviticus'], ['Pesachim', 'Rashi on Pesachim']

                                               ]):
                        count = False
                    elif row[2] in ['ein mishpat / ner mitsvah', 'automatic mesorat hashas']:
                        count = False
                    s_refs = []
                    num_ref_str = []
                    for ref in refs:
                        ref = ref.replace('Ralbag on Iyov', 'Ralbag on Job')
                        ref = ref.replace('Rashi on Num ', 'Rashi on Numbers ')
                        if txt_in_partial_list(ref, ignore_list):
                            ignore = True
                            continue
                        s = ref.split(' ')
                        try:
                            if ref in self.toc_data["reverse_index"] or ref+', ' in self.toc_data["reverse_index"]:  # no digit in end, use all
                                key = ref
                                num_ref = ''
                            else:
                                key = ' '.join(s[:-1])
                                num_ref = s[-1]
                            if key not in self.toc_data["reverse_index"]:
                                key += ', '
                            _id = self.toc_data["reverse_index"][key]

                        except KeyError as e:
                            logger.error("key not found: " + key)
                            raise e
                        if '-' in num_ref:
                            logger.debug("- in ref {}".format(ref))
                            num_ref = num_ref.split('-')[0]
                        res_num_ref = []
                        for part_num_ref in num_ref.split(':'):
                            if part_num_ref and part_num_ref[-1] in ['a', 'b']:
                                part_num_ref = str(int(part_num_ref[:-1]) * 2 - 2 + {"a": 1, "b": 2}[part_num_ref[-1]])
                            res_num_ref.append(part_num_ref)
                        num_ref_str.append(':'.join(res_num_ref))
                        s_refs.append([str(_id)] + res_num_ref)
                    if ignore:
                        continue
                    if count and (num_ref_str[0] == num_ref_str[1] or ((len(num_ref_str[1].split(':')) > 1 and
                                    len(num_ref_str[0].split(':')) > 1) and self.compare_lists_start(s_refs[0][1:],
                                                                                                     s_refs[1][1:]))):
                        for a, b in [(s_refs[0][0], s_refs[1][0]), (s_refs[1][0], s_refs[0][0])]:
                            if b in direct_comment and direct_comment[b] == a:
                                ignore = True
                                break
                        if ignore:
                            continue
                        for a, b in [(s_refs[0], s_refs[1]), (s_refs[1], s_refs[0])]:
                            if int(a[0]) in self.toc_data['commentary']:
                                if int(b[0]) in self.toc_data['commentary'][int(a[0])]:
                                    if self.toc_data['commentary'][int(a[0])][int(b[0])] in [COM_ONE_ON_ONE,
                                                                                             COM_ONE_ON_ONE_DICT,
                                                                                             COM_ONE_ON_ONE_DICT_EMPTY]:
                                        direct_comment[b[0]] = a[0]
                                        logger.warning("one by one verified {}".format(row))
                                        ignore = True
                                        break
                                    else:
                                        logger.warning("one by one cahp wrong comment type: {}? "
                                                       "not verified {}".format(self.toc_data['commentary'][int(a[0])][int(b[0])], row))
                        if not ignore:
                            logger.warning("one by one not verified? {}".format(row))
                    #elif num_ref_str[0] in num_ref_str[1] or num_ref_str[1] in num_ref_str[0]:
                    #    logger.warning("one by one? {}".format(row))
                    if count and ((len(num_ref_str[1].split(':')) > 1 and \
                           len(num_ref_str[0].split(':')) > 1) and \
                              (num_ref_str[0].startswith(':'.join(s_refs[1][1:-1])) or \
                                        num_ref_str[1].startswith(':'.join(s_refs[1][1:-1])))):
                        for a, b in [(s_refs[0][0], s_refs[1][0]), (s_refs[1][0], s_refs[0][0])]:
                            if b in chapter_direct_comment and chapter_direct_comment[b] == a:
                                count = False
                                break
                        if ignore:
                            continue
                        for a, b in [(s_refs[0], s_refs[1]), (s_refs[1], s_refs[0])]:
                            if int(a[0]) in self.toc_data['commentary']:
                                if int(b[0]) in self.toc_data['commentary'][int(a[0])]:
                                    if self.toc_data['commentary'][int(a[0])][int(b[0])] == COM_CHAP_LEVEL:
                                        if b[1:-1] == a[1:len(b[1:-1])+1]:
                                            chapter_direct_comment[b[0]] = a[0]
                                            logger.warning("one by one chapter verified {}".format(row))
                                            count = False
                                            break

                                        else:
                                            logger.warning("one by one chapter mark failed{}".format(row))
                    if not ignore:
                        if count and [row[3], row[4]] not in ignore_pairs:
                            pairs[(s_refs[0][0], s_refs[1][0])].append(row)
                            if row[3] not in not_direct_commentary + collective_not_direct_commentary:
                                if len(pairs[(s_refs[0][0], s_refs[1][0])]) > 100:
                                    logger.error("too many pairs: {}".format([row[3], row[4]]))
                                    # print [row[3], row[4]]
                                    ignore_pairs.append([row[3], row[4]])
                        self.insert_ref(s_refs[0], s_refs[1])
                        self.insert_ref(s_refs[1], s_refs[0])
                        valid_link_count += 1
        logger.info("link count: {} valid link count: {}".format(link_count, valid_link_count))
        for r in self.refs:
            json.dump(self.refs[r], open("{}/{}.ref.json".format(self.json_dir, r), 'w+'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", help="pdb on failure",
                        action="store_true", dest="debug")
    parser.add_argument("--json", help="get jsons from export",
                        action="store_true", dest="get_json")
    parser.add_argument("--ext-links", help="only ext links",
                        action="store_true", dest="ext_links")
    parser.add_argument("--only-comment", help="only comments",
                        action="store_true", dest="only_comment")
    parser.add_argument("--sefaria-path", help="sefaria export path",
                        default=TOC.DEFAULT_PATH, dest="path")
    parser.add_argument("--dest-path", help="json dest",
                        default='/tmp/json', dest="dest")
    args = parser.parse_args()
    if args.debug:
        import autodebug

    sef_logger()
    if args.only_comment:
        toc = pickle.load(open("toc.pickle"))
        toc.walk_on_commentary()
        toc.dump_toc_data()
        pickle.dump(toc, open("toc.pickle", "wb"))
        return

    if args.ext_links:
        toc = pickle.load(open("toc.pickle"))
        toc.get_refs()
        toc.dump_toc_data()
        pickle.dump(toc, open("toc.pickle", "wb"))
        return


    toc = TOC(args.path, args.dest)
    pickle.dump(toc, open("toc.pickle", "wb"))
    toc.walk_on_toc()
    pickle.dump(toc, open("toc.pickle", "wb"))
    logger.debug("walking on commentary")
    toc.walk_on_commentary()
    pickle.dump(toc, open("toc.pickle", "wb"))
    toc.get_refs()
    pickle.dump(toc, open("toc.pickle", "wb"))
    toc.dump_toc_data()


if __name__ == '__main__':
    main()