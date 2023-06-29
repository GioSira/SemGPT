from it.unito.db.query_semagram import *
from it.unito.prompt.categories_to_prompt import category2prompt, get_all_categories

def stats_by_category():
    categories = get_all_categories()
    stats = {}
    for category in categories:
        stats[category] = len(get_concepts_by_category(category))

    return stats

def stats_avg_filler_slot():
    categories = get_all_categories()
    stats = {}
    for category in categories:
        res = get_count_slot_value(category)
        count_slots = get_count_slots(category)
        for val in res:
            filler=val[0][1]
            slot=val[0][0]
            pos = val[0][2]
            count_val=val[1]
            count_slot = 0
            for count in count_slots:
                if count[0]==slot:
                    count_slot=count[1]
                    break
            for val2 in res: 
                if val2[0][0]==slot and val2[0][1]==filler and val2[0][2]!=pos:
                    count_val+=val2[1]
            avg = count_val /count_slot
            stats[category] = avg

    
    return stats





def stats_filler(): # numero di valori per categoria
    categories = get_all_categories()
    stats = {}
    for category in categories:
        res = get_count_values(category)
        sum_res = sum([r[1] for r in res])
        stats[category] = sum_res

    return stats
    

def stats_avg_slot_concept():
    categories = get_all_categories()
    stats = {}
    for category in categories:
        concepts = get_concepts_by_category(category)
        slots_concept = 0
        for concept in concepts:
            all_semagrams = get_all_concept_slots_and_values(concept)
            slots = set([s[0] for s in all_semagrams])
            len_slots = len(slots)
            slots_concept += len_slots
    
        stats[category] = slots_concept / len(concepts)

    return stats

if __name__ == '__main__':
    stats_cat = stats_by_category()
    print(stats_cat)

    stats_fil = stats_filler()
    print(stats_fil)

    stats_avg = stats_avg_filler_slot()
    print(stats_avg)

    stats_avg_slot = stats_avg_slot_concept()
    print(stats_avg_slot)
