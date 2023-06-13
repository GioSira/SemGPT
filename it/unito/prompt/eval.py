
from it.unito.db import query_semagram as qs

def evaluation(category, slot, value, results = None):
    # results è il risultato restituito dal llm
    
    # fare query sul db: 
    # 1. prendere tutti gli elementi della categoria
    # 2. mantenere solo gli elementi che hanno quello slot-value 

    concepts_category = qs.get_concepts_by_category(category)
    concepts_eval = qs.get_concept_with_slot_value(concepts_category, slot, value)

    # 3. precision e recall rispetto a results

    already_known = set(results).intersection(set(concepts_eval))

    precision = len(already_known) / len(results)
    recall = len(already_known) / len(concepts_eval)

    print(concepts_eval)
    print(results)
    print(already_known)
    print(precision)
    print(recall)


if __name__ == '__main__':
    evaluation("animals", "time", "summer")