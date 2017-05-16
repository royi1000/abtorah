import json
from collections import defaultdict
from sefaria.model import *
from sefaria.utils.hebrew import hebrew_term
import sefaria.system.database as database
import sefaria.summaries as sefsum



index = 0
books_index = {}
books_section_type = {}
hebrew_index = {}
reverse_index = {}
commentary = defaultdict(list)
commentary_description = []
reverse_commentary_description = {}
section_type = []

def safe_list_get (l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

def get_section_type(en):
    for i in range(len(section_type)):
        if en == section_type[i][0]:
            return i
    he = map(hebrew_term, en)
    section_type.append((en, he))
    return len(section_type)-1
    
def get_commentary_description(en, he):
    if en not in reverse_commentary_description:
        reverse_commentary_description[en] = len(commentary_description)
        commentary_description.append([en, he])
    return reverse_commentary_description[en]

def get_index():
    global index
    index += 1
    return index

def toc_to_xml(xml_file_name='toc.xml',write_text_jsons=True):
    toc = sefsum.get_toc()
    xml=open(xml_file_name, 'w+')
    level = 1
    xml.write('<?xml version="1.0" ?>\n<index name="onyourway">\n')
    for node in toc:
        handle_node(node,xml, level, write_text_jsons)
    j=open('main.json','w+')
    d=dict(hebrew_index=hebrew_index,books_index=books_index,reverse_index=reverse_index,commentary=commentary,commentary_description=commentary_description, section_type=section_type,books_section_type=books_section_type)
    j.write(json.dumps(d))
    xml.write('</index>')

def handle_complex(child, xml, level, comment=False, write_text_jsons=False):
    if type(child) == SchemaNode:
        xml.write('{}<node n="{}" en="{}">\n'.format(' '*4*level,child.title_group.primary_title('he').encode('utf-8').replace('"', "''"), child.title_group.primary_title('en')))
        for c in child.children:
            handle_complex(c, xml, level+1, comment,write_text_jsons=write_text_jsons)
        xml.write(' '*4*level + '</node>\n')
    else:
        s_index = sefsum.get_index(child.full_title())
        ind = get_index()
        books_index[ind] = child.full_title()
        reverse_index[child.full_title()] = ind
        if comment:
            commentary[reverse_index[child.full_title().split(' on ')[-1]]].append([ind, get_commentary_description(s_index.commentator, s_index.heCommentator)])
        he = child.title_group.primary_title('he').encode('utf-8').replace('"', "''")
        hebrew_index[ind] = he
        he_cont = TextChunk(Ref(child.full_title()), 'he').text
        en_cont = TextChunk(Ref(child.full_title()), 'en').text
        chapters = max(len(he_cont),len(en_cont))
        xml.write('{}<node n="{}" c="{}" en="{}" i="{}" d="{}"/>\n'.format(' '*4*level, he, chapters,  child.title_group.primary_title('en'), ind, get_section_type(child.sectionNames)))
        books_section_type[ind] = get_section_type(child.sectionNames)
        if write_text_jsons:
            for i in range(chapters):
                d = {'he': safe_list_get(he_cont, i, list()), 'en': safe_list_get(en_cont, i, list())}
                j=open('json/j{}-{}.json'.format(ind, i),'w+')
                j.write(json.dumps(d))
                j.close()

def handle_node(node,xml,level, write_text_jsons=False):
    if 'category' in node:
        xml.write('{}<node n="{}" en="{}">\n'.format(' '*4*level,node[u'heCategory'].encode('utf-8').replace('"', "''"), node[u'category']))
        for n in node[u'contents']:
            handle_node(n,xml,level+1, write_text_jsons)
        xml.write(' '*4*level + '</node>\n')
    else:
        s_index = sefsum.get_index(node[u'title'])
        if s_index.is_complex():
            xml.write('{}<node n="{}" en="{}">\n'.format(' '*4*level,Ref(node[u'title']).he_normal().encode('utf-8').replace('"', "''"), node[u'title']))
            for child in s_index.nodes.children:
                handle_complex(child, xml, level+1, s_index.is_commentary(),write_text_jsons=write_text_jsons)
            xml.write(' '*4*level + '</node>\n')
            return
        ind = get_index()
        books_index[ind] = node[u'title']
        reverse_index[node[u'title']] = ind
        if s_index.is_commentary():
            commentary[reverse_index[s_index.commentaryBook]].append([ind, get_commentary_description(s_index.commentator, s_index.heCommentator)])
        he = node[u'heTitle'].encode('utf-8').replace('"', "''")
        hebrew_index[ind] = he
        he_cont = TextChunk(Ref(node[u'title']), 'he').text
        en_cont = TextChunk(Ref(node[u'title']), 'en').text
        chapters = max(len(he_cont),len(en_cont))
        xml.write('{}<node n="{}" c="{}"  en="{}" i="{}" d="{}"/>\n'.format(' '*4*level,he, chapters, node[u'title'], ind, get_section_type(Ref(node[u'title']).index.nodes.sectionNames)))
        books_section_type[ind] = get_section_type(Ref(node[u'title']).index.nodes.sectionNames)
        if write_text_jsons:
            for i in range(chapters):
                d = {'he': safe_list_get(he_cont, i, list()), 'en': safe_list_get(en_cont, i, list())}
                j=open('json/j{}-{}.json'.format(ind, i),'w+')
                j.write(json.dumps(d))
                j.close()
            
def page_to_number(page):
    if 'a' in page or 'b' in page:
        amud = page[:-1]
        page = int(page[:-1]) * 2
        if amud == 'a':
            page = page - 1 
    return page
    
def get_ref_array(ref, reverse_index):
    n_range = 0
    name = ' '.join(ref.split(' ')[:-1])
    n_id = reverse_index[name]
    n_index = ref.split(' ')[-1]
    if '-' in n_index:
        n_range = n_index.split('-')[1]
        if ':' in n_range:
            n_range = 0
        else:
            n_range = page_to_number(n_range)
        n_range = int(n_range)
        n_index = n_index.split('-')[0]
    n_index = map(page_to_number, n_index.split(':'))
    n_index = map(int, n_index)
    if n_range:
        n_range = n_range - n_index[-1]
    # normalize to text array index
    #n_index = map(lambda x:x-1, n_index)
    return [n_id, n_index, n_range]

def add_index_to_ref(ref1, ref2, refs):
    if ref1[0] not in refs:
        refs[ref1[0]] = {}
    ref = refs[ref1[0]]
    for i in ref1[1][:-1]:
        if i not in ref:
            ref[i]={}
        ref=ref[i]
    if ref1[1][-1] not in ref:
        if isinstance(ref, list):
            tmp_ref = ref
            ref = {}
            ref[0] = tmp_ref
        ref[ref1[1][-1]] = []    
    if isinstance(ref[ref1[1][-1]], dict):
        ref = ref[ref1[1][-1]]
        if 0 not in ref:
            ref[0] = []
        ref[0].append(ref2)
    else:
        ref[ref1[1][-1]].append(ref2)
    
def get_links(f):
    j = json.loads(open(f).read())
    books_index = j['books_index']
    reverse_index = j['reverse_index']
    refs = {}
    for k in reverse_index:
        #book_id = reverse_index[k]
        links = LinkSet(Ref(k)).array()
        for link in links:
            link_refs = link.refs
            if (link_refs[0] in link_refs[1]) or (link_refs[1] in link_refs[0]):
                continue
            try:
                r_array = get_ref_array(link_refs[0], reverse_index)
                l_array = get_ref_array(link_refs[1], reverse_index)
            except KeyError:
                print "failed get name of link: {}".format(link_refs)
                continue
            add_index_to_ref(r_array, l_array, refs)
            add_index_to_ref(l_array, r_array, refs)
    for k in refs:
        j=open('json/r{}.json'.format(k),'w+')
        j.write(json.dumps(refs[k]))
        j.close()
        
def main():
    toc_to_xml()

if __name__ == '__main__':
    main()
