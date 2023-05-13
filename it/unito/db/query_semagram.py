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
    return [(r["slot"], r["value"], r["pos"], r["syn"]) for r in res] # TODO: togliere generalization e specialization


def get_count_slots(category):

    result_freq = sem_collection.aggregate(
        [
            {
                "$match": {
                    "concept": {
                        "$in": get_concepts_by_category(category)
                    }
                }
            },{
                "$group": {
                    "_id": "$slot",
                    "count": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "count": -1
                }
            }
        ]

    )

    return [(r['_id'], r['count']) for r in result_freq]

def get_count_values(category):

    result_freq = sem_collection.aggregate(
        [
            {
                "$match": {
                    "concept": {
                        "$in": get_concepts_by_category(category)
                    }
                }
            },{
                "$group": {
                    "_id": "$value",
                    "count": {
                        "$sum": 1
                    }
                }
            }, {
                "$sort": {
                    "count": -1
                }
            }
        ]

    )

    return [(r['_id'], r['count']) for r in result_freq]

def get_count_slot_value(category):

    result_freq = sem_collection.aggregate(
        [
            {
                "$match": {
                    "concept": {
                        "$in": get_concepts_by_category(category)
                    }
                }
            },{
                "$group": {
                    "_id": {
                        "slot": "$slot",
                        "value": "$value"
                    },
                    "count": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "count": -1
                }
            }
        ]

    )

    return [([r["_id"]["slot"], r["_id"]["value"]], r["count"]) for r in result_freq]


