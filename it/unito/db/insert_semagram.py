from it.unito.db import dbname, sem_collection, category_collection
from it.unito.semagram.concepts import categories_dict
from it.unito.semagram.semagram_loader import read_xml
import bson


def insert_semagram(sem_base):

    item_list = []
    for concept in sem_base.getAllConcepts():
        for (slot, value, pos, syn) in sem_base.getConceptValues(concept):

            item = {
                "_id": bson.ObjectId(),
                "concept": concept,
                "slot": slot,
                "value": value,
                "pos": pos,
                "syn": syn
            }

            item_list.append(item)

    sem_collection.insert_many(item_list)


def insert_categories(cat_dict):

    item_list = []
    for cat in list(cat_dict.keys()):
        for concept in cat_dict[cat]:
            item = {
                "_id": bson.ObjectId(),
                "category": cat,
                "concept": concept
            }
            item_list.append(item)

    category_collection.insert_many(item_list)


if __name__ == '__main__':

    s = read_xml('/Users/giovanni/PycharmProjects/SemagramGPT/semagrams_300.xml')

    insert_semagram(s)
    insert_categories(categories_dict)