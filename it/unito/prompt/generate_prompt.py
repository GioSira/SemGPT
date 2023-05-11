from it.unito.prompt.slots_to_prompt import slot2prompt, value2prompt
from it.unito.prompt.categories_to_prompt import category2prompt
from it.unito.semagram.concepts import categories_dict
from random import choices, randint
from it.unito.db.query_semagram import *


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


def __select_random_concepts(list_of_concepts):

    num_concepts = randint(1, 10)
    return choices(list_of_concepts, k=num_concepts)


def __select_random_slots(list_of_slots):

    num_slots = randint(5, 10)
    slots = choices(list_of_slots, k=num_slots)
    return slots


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


if __name__ == '__main__':

    prompt = generate_prompt_db(10, 'animals')
    print(prompt)

