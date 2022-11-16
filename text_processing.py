from googletrans import Translator
import re
from Levenshtein import distance as lev

def compare_text(a, b):
    a = rm_spaces(a).replace(" ", "")
    b = rm_spaces(b).replace(" ", "")

    return lev(a, b)

def translate(text, src, dest):
    translator = Translator()
    result = translator.translate(text, src=src, dest=dest)
    return result


def rm_special_characters(t):
    t = t.replace(";", " ")
    t = t.replace("(", " ")
    t = t.replace(")", " ")

    return t


def rm_spaces(t):
    t = t.lstrip()
    t = t.rstrip()
    t = re.sub('\s+', ' ', t, re.DOTALL)
    return t


def get_epic_number(t):
    t = t.split('\n')
    t = list(filter(lambda x: x != '' and re.match(r"\s+", x) == None, t))

    if t:
        return rm_spaces(t[0])

    return None


def get_name(t):
    deli = t.find(':')
    if deli != -1:
        return rm_spaces(t.split(':')[1])

    m = re.match(".*name(?P<name>.+)", t, re.IGNORECASE)

    if m and 'name' in m.groupdict():
        return rm_spaces(m['name'])

    return None


def get_relation(t):
    relation_type = "spouse"
    rel_re = re.search(r"father", t, re.IGNORECASE)

    if rel_re:
        relation_type = "father"

    deli = t.find(':')
    if deli != -1:
        return relation_type, rm_spaces(t.split(':')[1])

    m = re.match(".*name(?P<name>.+)", t, re.IGNORECASE)

    if m and 'name' in m.groupdict():
        return relation_type, rm_spaces(m['name'])

    return None


def get_house(t):
    deli = t.find(':')
    if deli != -1:
        return rm_spaces(t.split(':')[1])

    m = re.match(".*house.*(no|number)\.*(?P<h_name>.+)", t, re.IGNORECASE)

    if m and 'h_name' in m.groupdict():
        return rm_spaces(m['h_name'])

    return None


def get_age_gender(t):
    gender = "male"
    age = None

    gender_re = re.search(r"female", t, re.IGNORECASE)
    age_re = re.search(r"\d+", t)

    if gender_re:
        gender = "female"

    if age_re:
        age = age_re.group()

    return age, gender


def create_search_id_1(*argv):
    id = ''
    for arg in argv:
        if arg:
            t = rm_spaces(arg)
            id = id + ' ' + t.lower() + ' ' + t.lower().replace(' ', '')

    id = id.lstrip()
    return id


def create_search_id_2(*argv):
    id = ''
    for arg in argv:
        if arg:
            id = id + ' ' + rm_spaces(arg).lower().replace(' ', '')

    id = id.lstrip()
    return id


def process_electoral_data(text_dump):
    t = text_dump.split('\n')
    t = list(filter(lambda x: x != '' and re.match(r"\s+", x) == None, t))
    i = 0
    if i + 4 >= len(t):
        return None

    name = get_name(t[i+1])
    relation_name = get_relation(t[i+2])
    house = get_house(t[i+3])
    age, gender = get_age_gender(t[i+4])

    di = {}

    if name:
        di['name'] = name
    else:
        return None

    if house:
        di['house'] = house

    else:
        return None

    if relation_name:
        di['relation'] = {
            "type": relation_name[0],
            "name": relation_name[1],
            "s_id_1": create_search_id_1(relation_name[1], di['house']),
            "s_id_2": create_search_id_2(relation_name[1], di['house'])
        }
    else:
        di['relation'] = None


    if age:
        di['age'] = age

    if gender:
        di['gender'] = gender

    di['s_id_1'] = create_search_id_1(di['name'], di['house'])
    di['s_id_2'] = create_search_id_2(di['name'], di['house'])

    return di
