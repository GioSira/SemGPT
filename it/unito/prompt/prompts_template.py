

def one_shot_template_slot_value(category, slot, value):

    prompt = f"Find {category} that meet the criteria in the text below.  Avoid any adjective in the list. \n \
        Desired output: <comma_separated_list> \n \
        Text: they {slot} {value}." 

    # TODO: COME GESTISCO GLI ESEMPI NELL'ELENCO PUNTATO? 
    return prompt

def few_shot_template_slot_value(category, slot, value): 

    # TODO: implementare few shot template
    pass