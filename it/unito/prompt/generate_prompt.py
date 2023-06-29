from it.unito.prompt.slots_to_prompt import slot2prompt, value2prompt
from it.unito.prompt.categories_to_prompt import category2prompt, get_all_categories
from it.unito.semagram.concepts import categories_dict
from it.unito.prompt.prompts_template import zero_shot_template_slot_value
from random import choices, randint, choice
from it.unito.db.query_semagram import *
import math
import json

def __list2string(key, elems):

    elems = list(elems)
    if len(elems) == 1:
        vl = elems[0]
    elif len(elems) == 2:
        vl = " or ".join(elems)
    else:
        vl = ", ".join(elems[:-1]) + " or " + elems[-1]

    if key == "sound":
        return f"have {vl} {key}"
    else:
        return vl


def __list2prompt(slot_value_list):

    d = {}
    for (slot, value, pos, _) in slot_value_list:
        slot_prompt = slot2prompt(slot, pos)
        value_prompt = value2prompt(value, slot)
        d.setdefault(slot_prompt, set())
        d[slot_prompt].add(value_prompt)

    prompt_list = []
    for k in list(d.keys()):
        elems = d[k]
        vl = __list2string(k, elems)
        prompt_list.append(f"{k} {vl}")

    return "; ".join(prompt_list[:-1]) + "; and " + prompt_list[-1]


def __pair2prompt(slot, value, pos):

    slot_prompt = slot2prompt(slot, pos)
    value_prompt = value2prompt(value, slot)

    return f"{slot_prompt} {value_prompt}"


def __select_random_concepts(list_of_concepts):

    num_concepts = randint(1, 10)
    return choices(list_of_concepts, k=num_concepts)


def __select_random_slots(list_of_slots):

    num_slots = randint(5, 10)
    slots = choices(list_of_slots, k=num_slots)
    return slots

def __select_random_value(list_of_tuples, slot_chosen):
    list_of_values = []

    for slot, value, pos, _ in list_of_tuples:
        if slot == slot_chosen:
            list_of_values.append((value, pos))

    return choice(list_of_values)
    

def generate_prompt(num_elems, category, semagram_base):

    concepts = categories_dict[category]
    selected_concepts = __select_random_concepts(concepts)

    slot_value_pos_syn_tuples = semagram_base.getConceptsValues(selected_concepts)
    selected_slots = __select_random_slots(slot_value_pos_syn_tuples)

    value_prompt = __list2prompt(selected_slots)

    category_string = category2prompt(category)

    prompt = f"give me a list of {num_elems} {category_string}, separated by comma, " \
             f"that meet at least one of the following criteria: {value_prompt}"

    return prompt


def generate_prompt_db(num_elems, category):

    concepts = get_concepts_by_category(category)
    selected_concepts = __select_random_concepts(concepts)

    tuple_list = set()
    for c in selected_concepts:
        svps_concept_tuples = get_all_concept_slots_and_values(c)
        tuple_list.update(svps_concept_tuples)

    selected_slots = __select_random_slots(list(tuple_list))

    value_prompt = __list2prompt(selected_slots)
    category_string = category2prompt(category)

    prompt = f"give me a list of {num_elems} {category_string}, separated by comma, " \
             f"that meet at least one of the following criteria: {value_prompt}"

    return prompt

def generate_prompt_slot_value(num_elem, category, slot, value, pos):
    value_prompt = value2prompt(value, slot)
    category_string = category2prompt(category)
    slot_prompt = slot2prompt(slot, pos, category)

    prompt = zero_shot_template_slot_value(num_elem, category_string, slot_prompt, value_prompt)

    return prompt


def generate_prompt_ranking(num_elems, category, ranking):
    
    slot = ranking[0][0]
    value, pos = __select_random_value(ranking, slot)


    value_prompt = __pair2prompt(slot, value, pos)
    category_string = category2prompt(category)

    prompt = f"give me a list of {num_elems} {category_string}, separated by comma, " \
             f"that meet at least one of the following criteria: {value_prompt}"

    return prompt



def get_count(counts, val, pos):

    for [v, p], c in counts:
        if v == val and p == pos:
            return p, c
            
def get_count_slot(counts, slot):

    for v, c in counts:
        if v == slot:
            return c

def pmi_slot_value_by_category(category):
    """
    Calculate the PMI between value of field 'slot' and value of field 'value' in the semagram collection of the 'category'.
    """

    count_slots = get_count_slots(category)
    count_values = get_count_values(category)

    co_occurrence = get_count_slot_value(category)

    pmis = []

    total_semagram_category = 0

    for _, count in count_slots:
        total_semagram_category += count

    print("total pair slot-value: " + str(total_semagram_category) + " for category: " + category)

    for [slot, value, pos], count_slot_value in co_occurrence:
        count_slot = get_count_slot(count_slots, slot)
        pos, count_value = get_count(count_values, value, pos)
        pmi = math.log2((count_slot_value / total_semagram_category) / 
                        ((count_slot / total_semagram_category) * (count_value / total_semagram_category)))
        pmis.append(([slot, value, pos], pmi))

    pmis.sort(key= lambda x: x[1], reverse=True)

    path = f"it/data/{category}/pmi_{category}.txt"
    with open(path, "w", encoding="utf8") as f:
        for [slot, value, pos], pmi in pmis:
            f.write(f"{slot}\t{value}\t{pos}\t{pmi}\n")

    return pmis, count_slots, count_values, co_occurrence
    

def get_slot_value_to_ask(concept):
    
    path = f"it/data/{concept}/ranking.txt"
    slot_values = []
    with open(path, "r", encoding="utf8") as f:
    
        for line in f.readlines():
            slot, value, pos, rank = line.split("\t")
            slot_values.append((slot, value, pos, rank))

    return slot_values

def clean_gen_spec(ranking): 

    for slot, value, pos, rank in ranking: 
        if slot == "generalization" or slot == "specialization": 
            ranking.remove((slot, value, pos, rank))

if __name__ == '__main__':

    
    categories = get_all_categories()

    prompts = []
    
    for category in categories:
        
        """
        print("category: " + category)
        ranking = get_slot_value_to_ask(category) 

        clean_gen_spec(ranking)

        prompt = generate_prompt_ranking(10, category, ranking)

        print(prompt)
        """
        # TODO: pmi da fare in ordine opposto?
        pmis, count_slots, count_values, co_occurence  = pmi_slot_value_by_category(category)

        # crea il prompt per ognuno

        for pmi in pmis: 
            slot, value, pos = pmi[0]
            prompt_text = generate_prompt_slot_value(10, category, slot, value, pos)
            prompt = {
                "cat": category, 
                "slot": slot,
                "value": value,
                "prompt": prompt_text}
            
            prompts.append(prompt)

    # salva lista in un file json
    with open("it/data/prompts.json", "w", encoding="utf8") as f:
        json.dump(prompts, f, indent=4, ensure_ascii=False)
        

    #qty = 10

    #prompt = generate_prompt_db(qty, category)
    #print(prompt)
 
 