from it.unito.db import sem_collection, category_collection, dbname


def get_concepts_by_category(category):

    q = {"category": category}
    results = category_collection.find(q)

    return [r["concept"] for r in results]


def query_by_concept(concept):

    q = {"concept": concept}
    results = sem_collection.find(q)

    return results


def query_by_slot(slot):

    q = {"slot": slot}
    results = sem_collection.find(q)

    return results


def query_by_concept_and_slot(concept, slot):

    q = {"concept": concept, "slot": slot}
    results = sem_collection.find(q)

    return results


def get_all_slot_types():

    results = sem_collection.distinct('slot')
    return results


def get_all_concepts():

    results = sem_collection.distinct('concept')
    return results


def get_all_concept_slots_and_values(concept):

    res = query_by_concept(concept)
    return [(r["slot"], r["value"], r["pos"], r["syn"]) for r in res]
