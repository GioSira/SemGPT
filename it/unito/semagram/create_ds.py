from it.unito.db.query_semagram import get_all_concepts_obj, query_by_concept
from it.unito.prompt.slots_to_prompt import *
import pickle

if __name__ == '__main__':  

    concepts = get_all_concepts_obj()
    print(concepts.count_documents({}))

    # 1. creo un dataset con tutte le frasi 
    sentences = []
    sentences_parts = []
    for concept in concepts.find():
        semagrams = query_by_concept(concept['concept'])
        for semagram in semagrams: 
            #print(semagram)
            concept_name = semagram['concept']
            slot_name = semagram['slot']
            value_name = semagram['value']
            pos = semagram['pos']
            category = concept['category']

            slot = Slots.from_str(slot_name)
            if slot == Slots.BODY_PART or slot == Slots.SMELL or (slot == Slots.HOW_TO_USE and (pos == 'N' or (pos == 'V' and category == "food"))) or \
                  slot == Slots.PLACE or slot == Slots.USER or slot == Slots.GROUP or slot == Slots.SOUND or \
                    (slot == Slots.TIME and category != "animals") or slot == Slots.ACCESSORY or concept_name == value_name:
                continue
            #print(concept_name, slot2prompt(slot_name, pos, category), value2prompt(value_name, slot_name))
            #print(slot_name, pos, category, slot_name == Slots.BODY_PART)
            sentence = 'The ' + concept_name + ' ' + slot2promptEasy(slot_name, pos, category) + ' ' + value2prompt(value_name, slot_name)
            semagram_parts = [concept_name, slot2promptEasy(slot_name, pos, category), value2prompt(value_name, slot_name), slot]
            
            sentences_parts.append(semagram_parts)
            sentences.append(sentence)

    print(len(sentences))
    print(len(sentences_parts))

    print(sentences[0], sentences_parts[0])

    # dataset to mask
    with open('dataset_semagram.txt', 'w', encoding='utf8') as f:
        for sentence in sentences:
            f.write(sentence + '\n')
    
    with open('dataset_semagram_parts.txt', 'w', encoding='utf8') as f:
        for sentence in sentences_parts:
            f.write(' '.join(sentence[:3]) +" "+ str(sentence[3]) + '\n')
    
    # parts 
    with open('dataset_semagram_parts', 'wb') as fp:
        pickle.dump(sentences_parts, fp)


    

