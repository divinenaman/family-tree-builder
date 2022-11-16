from cv2 import threshold
from numpy import in1d, reciprocal
import db
from bson.son import SON
from Levenshtein import distance as lev
import family_relationships


def search_similar_nodes(db, exclude_node_ids, pc, ac, part, text):
    pipeline = [
        {"$match": {"$text": {"$search": text}}},
        {"$set": {"score": {"$meta": "textScore"}}},
        {"$match": SON([("_id", {"$nin": exclude_node_ids}), ("pc", pc),
                       ("ac", ac), ("part_number", part)])},
        {"$sort": SON([("score", -1)])},
        {"$limit": 1}
    ]

    return list(db['dump_data'].aggregate(pipeline))


def create_node(db, data):
    res = db['dump_data'].insert_one(data)
    return res


def get_node_by_id(db, id):
    res = db['dump_data'].find_one({"_id": id})
    return res


def add_link_by_id(db, id, linked_id, linked_s_id, link_type, reciprocal_link_type=""):
    res = db['dump_data'].update_one({"_id": id}, {
                                     "$push": {"links": {"id": linked_id, "s_id_1": linked_s_id, "type": link_type, "reciprocal_type": reciprocal_link_type}}})
    return True



def rm_self_links(db):
    pipeline = [{"$set": {"links": {"$filter": {"input": "$links",
                                                "as": "a", "cond": {"$ne": ["$$a.id", "$_id"]}}}}}]
    db['dump_data'].update_many({}, pipeline)


def link_family(db, threshold=100, sort_field="age"):

    print("family-link: start")

    skip = 0
    limit = 1

    while skip < threshold:
        nodes = db['dump_data'].find({}).sort(sort_field, -1).skip(skip).limit(1)

        if not nodes:
            break

        res = link_direct_relation(db, nodes[0])
        link_indrect_relation(db, nodes[0]['_id'])

        skip += limit

    print(f"family-link: end (threshold = {threshold})")


def get_linked_nodes(node):
    linked_node_ids = set()

    # prevent indirect relation links
    if node.get('links'):
        for l in node['links']:
            linked_node_ids.add(l['id'])

    # prevent self link
    linked_node_ids.add(node['_id'])

    # prevent direct relation link if any
    if node.get('relation') and node['relation'].get('id'):
        linked_node_ids.add(node['relation']['id'])

    return linked_node_ids


def link_direct_relation(db, node):
    if 'relation' not in node or not node['relation']:
        return False

    if 'is_linked' in node['relation'] and node['relation']['is_linked'] == True:
        return True

    linked_nodes_ids = get_linked_nodes(node)
    res = search_similar_nodes(
        db, list(linked_nodes_ids), node["pc"], node["ac"], node["part_number"], node['relation']["s_id_1"])

    if not res or len(res) == 0:
        return False

    sim_node = res[0]

    sim_house_score = lev(node["house"], sim_node["house"])
    sim_name_score = lev(node["name"], sim_node["name"])

    if sim_house_score <= 1 and sim_name_score <= 4:

        link_type = node['relation']['type']
        reciprocal_link_type = "son"

        if link_type == "spouse":
            reciprocal_link_type = "spouse"
        elif node['gender'] == "female":
            reciprocal_link_type = "daughter"

        db['dump_data'].update_one({"_id": node['_id']}, {
                                   "$set": {"relation.is_linked": True, "relation.id": sim_node["_id"]}})

        add_link_by_id(db, sim_node["_id"], node['_id'],
                       node['s_id_1'], reciprocal_link_type, link_type)

        return True

    return False

def link_indrect_relation(db, node_id):

    # A
    node = get_node_by_id(db, node_id)

    linked_node_ids = get_linked_nodes(node)

    if not node['relation'] or 'is_linked' not in node['relation'] or node['relation']['is_linked'] == False:
        return False

    # B
    node_linked = get_node_by_id(db, node['relation']['id'])

    if not node_linked or not node_linked['links']:
        return False

    for link in node_linked['links']:

        if link['id'] in linked_node_ids:
            continue

        link_types = family_relationships.get_previous_generation_relationship(
            node['gender'], node['relation']['type'], link['type'], link['reciprocal_type'])

        if link_types != None:
            add_link_by_id(db, node['_id'], link['id'],
                           link['s_id_1'], link_types[0], link_types[1])
            add_link_by_id(db, link['id'], node['_id'],
                           node['s_id_1'], link_types[1], link_types[0])

            linked_node_ids.add(link['id'])


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    dbs = db.get_client()

    print(link_family(dbs))
