

def zero_shot_template_slot_value(num_elem, category, slot, value):
    prompt = f"Provide a list of {num_elem} words that belong to the category and satisfy the condition. \n\
        Desired output: comma separated list of words. \n\
        Category: {category}. \n\
        Condition: {slot} {value}. \n\
        Output: "
    
    return prompt

"""
prompt = f"Find {category} that meet the criteria in the text below.  Avoid any adjective in the list. \n \
        Desired output: <comma_separated_list> \n \
        Text: they {slot} {value}." 

    # TODO: COME GESTISCO GLI ESEMPI NELL'ELENCO PUNTATO?

    prompt = f"List items in singular that only meet all the criteria in the below text.  Avoid any adjective in the list. \
        Output: only comma separated list \
        Text: {category} that {slot} {value}. "
    
    prompt = f"List {category} in singular form that {slot} {value}.  Avoid any adjective in the list. "
"""

def one_shot_template_slot_value(category, slot, value):
    pass

def few_shot_template_slot_value(category, slot, value): 

    # TODO: implementare few shot template
    pass

