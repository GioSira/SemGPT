from it.unito.db import query_semagram as qs
import json

def evaluation(category, slot, value, results = None):
    # results è il risultato restituito dal llm
    
    # fare query sul db: 
    # 1. prendere tutti gli elementi della categoria
    # 2. mantenere solo gli elementi che hanno quello slot-value 

    concepts_category = qs.get_concepts_by_category(category) 
    concepts_eval = qs.get_concept_with_slot_value(concepts_category, slot, value)

    # 3. precision e recall rispetto a results

    if len(concepts_eval) == 0:
        print("No concepts found for the given slot-value")
        print("category: " , category)
        print("slot: " , slot)
        print("value: " , value)

    if len(results) == 0:
        precision = 0.0
        recall = 0.0

    else: 
        already_known = set(results).intersection(set(concepts_eval))

        precision = len(already_known) / len(results)
        recall = len(already_known) / len(concepts_eval)

        print("concepts_eval", concepts_eval)
        print("results: ", results)
        print("already_known ", already_known)
        print("precision ", precision)
        print("recall ", recall)

    return precision, recall

def read_results(file): 

    with open(file, "r", encoding='utf8') as f:
        results_str = f.readlines()

    results = []
    for i in range(len(results_str)):
        results.append(json.loads(results_str[i]))

    return results

def clean_results(results): 
    
    results_cleaned = []
    for result in results: 
        result_cleaned = []
        output = result["result"]
        #print("prima: ", output)
        output = output.strip(" \n`")
        #print("dopo: ", output)
        output = output.split("\"\"\"")[0]
        output = output.split("```")[0]
        #print("dopo2: ", output)

        contains_digit = False
        for ch in output:
            if ch.isdigit():
                contains_digit = True
                break

        if contains_digit:
            output = output.strip(" \n")
            enumerate = output.split("\n")
            for elem in enumerate: 
                enum = elem.strip()
                word = ""
                for ch in enum:
                    if not ch.isdigit() and ch != "." and ch != " ":
                        word += ch
                result_cleaned.append(word)
        else:
            for w in output.split(","):
                if w != "":
                    result_cleaned.append(w.strip(" \n."))
        
        result["result"] = result_cleaned 
        results_cleaned.append(result)

    #print("results_cleaned: ", results_cleaned)
    return results_cleaned

def evaluation_(list_to_eval):

    res = []
    for elem in list_to_eval:
        print(elem)
        category = elem["cat"]
        if category == "appliance, equipment and device":
            category = "appliance"
        elif category == "home item":
            category = "home"
        elif category == "music instrument":
            category = "instruments"
        elif category == "object":
            category = "artifacts"
        elif category != "food":
            category = category + "s"
        slot = elem["slot"]
        value = elem["value"]
        results = elem["result"]
        prec, rec = evaluation(category, slot, value, results)
        res.append((prec, rec))

    return res

if __name__ == '__main__':
    #evaluation("animals", "time", "summer")

    file = f"prompts_result__t_0.35__top_p_0.7__max_new_tokens_128.jsonl"

    results = read_results(file)

    cleaned_results = clean_results(results)

    print(cleaned_results)

    res = evaluation_(cleaned_results)

    print("\n\n FINAL RESULTS \n\n")
    print(res)
