from it.unito.db.query_semagram import get_all_concepts_obj
from it.unito.skeleton.slots import Slots
from nltk.corpus import wordnet as wn
import warnings
warnings.simplefilter("ignore")
import requests
import pickle
from collections import defaultdict 


def search_concepts_on_semagram(): 
    with open(f'dataset_semagram_parts', 'rb') as fp:
        semagrams = pickle.load(fp)

    print(semagrams[0])
    
    return semagrams

def search_concepts_on_wordnet(concepts): # ho il synset già da semagram
    synsets = []
    for concept in concepts.find():
        synset_str = concept["synset"]
        if synset_str != "":
            synsets.append((concept, wn.synset(synset_str)))
    return synsets

def search_concepts_on_conceptnet(concepts):
    concepts_cn = []
    for concept in concepts.find():
        concept_str = concept["concept"]
        concept_cn = requests.get(f"http://api.conceptnet.io/c/en/{concept_str}").json()
        concepts_cn.append(concept_cn)

    return concepts_cn

def relations_on_wordnet(synsets):
    relations = []
    for concept, synset in synsets:
        

        if synset.pos() == 'n':
            
            hypo_lemmas = []
            for hypo_synset in synset.hyponyms(): 
                for lemma in hypo_synset.lemmas():
                    if '_' in str(lemma.name()):
                        hypo_lemmas.append(str(lemma.name()).replace("_", " "))
                    else:
                        hypo_lemmas.append(str(lemma.name()))
            
            hypo_lemmas = list(set(hypo_lemmas))
            for hypo_lemma in hypo_lemmas:

                synset_lemmas = []
                for lemma in synset.lemmas():
                    if '_' not in str(lemma.name()) and len(str(lemma.name()).split()) == 1:
                        synset_lemmas.append(str(lemma.name()))
                
                synset_lemmas = list(set(synset_lemmas))
                
                if len(synset_lemmas) == 0: 
                    relation = ([concept['concept']], "hyponyms", hypo_lemma)
                    if relation not in relations:
                        relations.append(relation)
                else: 
                    relation = (synset_lemmas, "hyponyms", hypo_lemma)
                    if relation not in relations:
                        relations.append(relation)  # [tutte le lemmatizzazione del concetto], relazione, iponinmi

            hyper_lemmas = []
            for hyper_synset in synset.hypernyms():
                for lemma in hyper_synset.lemmas():
                    if '_' in str(lemma.name()):
                        hyper_lemmas.append(str(lemma.name()).replace("_", " "))
                    else:
                        hyper_lemmas.append(str(lemma.name()))
            
            hyper_lemmas = list(set(hyper_lemmas))
            for hyper_lemma in hyper_lemmas:
                synset_lemmas = []
                for lemma in synset.lemmas():
                    if '_' not in str(lemma.name()) and len(str(lemma.name()).split()) == 1:
                        synset_lemmas.append(str(lemma.name()))
                synset_lemmas = list(set(synset_lemmas))

                if len(synset_lemmas) == 0: 
                    relation = ([concept['concept']], "hypernyms", hyper_lemma)
                    if relation not in relations:
                        relations.append(relation)
                else: 
                    relation = (synset_lemmas, "hypernyms", hyper_lemma)
                    if relation not in relations:
                        relations.append(relation)

            # TODO: ULTERIORI STATISTICHE - da correggere per mascherare il primo concetto come per iperonimia e iponimia!
            #relations.append((concept, "member_holonyms", list(set(synset.member_holonyms()))))
            #relations.append((concept, "member_meronyms", list(set(synset.member_meronyms()))))
            #relations.append((concept, "part_holonyms", list(set(synset.part_holonyms()))))
            #relations.append((concept, "substance_meronyms", list(set(synset.substance_meronyms()))))
            #relations.append((concept, "substance_holonyms", list(set(synset.substance_holonyms()))))
                                    
            part_meronyms_lemmas = []
            for part_meronym_synset in synset.part_meronyms():
                for lemma in part_meronym_synset.lemmas():
                    if '_' in str(lemma.name()):
                        part_meronyms_lemmas.append(str(lemma.name()).replace("_", " "))
                    else:
                        part_meronyms_lemmas.append(str(lemma.name()))
                part_meronym_lemmas = list(set(part_meronyms_lemmas))

                synset_lemmas = []
                for lemma in synset.lemmas():
                    if '_' not in str(lemma.name()) and len(str(lemma.name()).split()) == 1:
                        synset_lemmas.append(str(lemma.name()))
                synset_lemmas = list(set(synset_lemmas))
                for part_meronym_lemma in part_meronym_lemmas:
                    if len(synset_lemmas) == 0: 
                        relation = ([concept['concept']], "part_meronyms", part_meronym_lemma)
                        if relation not in relations:
                            relations.append(relation)
                    else: 
                        relation = (synset_lemmas, "part_meronyms", part_meronym_lemma)
                        if relation not in relations:
                            relations.append(relation)

            
            
        elif synset.pos() == 'v':
            hyper_lemmas = []
            for hyper_synset in synset.hypernyms():
                for lemma in hyper_synset.lemmas():
                    if '_' in str(lemma.name()):
                        hyper_lemmas.append(str(lemma.name()).replace("_", " "))
                    else:
                        hyper_lemmas.append(str(lemma.name()))
            
            hyper_lemmas = list(set(hyper_lemmas))
            for hyper_lemma in hyper_lemmas:
                synset_lemmas = []
                for lemma in synset.lemmas():
                    if '_' not in str(lemma.name()) and len(str(lemma.name()).split()) == 1:
                        synset_lemmas.append(str(lemma.name()))
                synset_lemmas = list(set(synset_lemmas))
                if len(synset_lemmas) == 0: 
                    relation = ([concept['concept']], "hypernyms", hyper_lemma)
                    if relation not in relations:
                        relations.append(relation)
                else: 
                    relation = (synset_lemmas, "hypernyms", hyper_lemma)
                    if relation not in relations:
                        relations.append(relation)
    
    return relations

def relations_on_conceptnet(concepts_cn):
    relations = []
    for concept_cn in concepts_cn:
        for edge in concept_cn["edges"]:
            if edge["rel"]["label"] != "ExternalURL" and edge["rel"]["label"] != "Entails" and \
                edge["rel"]["label"] != "InstanceOf" and edge["start"]["language"] == "en" and edge["end"]["language"] == "en":
                
                start_list = edge["start"]["label"].split()
                end_list = edge["end"]["label"].split()

                relation_label = edge["rel"]["label"]
                name_concept = concept_cn["@id"].split("/")[3]
                start_label = edge["start"]["label"]
                end_label = edge["end"]["label"]

                if relation_label == "IsA":
                    if edge["end"]["label"] == name_concept: 
                        relation_label = "hyponym"
                        start_label = edge["end"]["label"]
                        end_label = edge["start"]["label"]
                        start_list = edge["end"]["label"].split()
                        end_list = edge["start"]["label"].split()

                if relation_label == "AtLocation": 
                    if edge["start"]["label"] == name_concept: 
                        continue
                    else: 
                        start_label = edge["end"]["label"]
                        end_label = edge["start"]["label"]
                        start_list = edge["end"]["label"].split()
                        end_list = edge["start"]["label"].split()

                if len(start_list) == 1: 
                    if len(end_list) == 1: # one word for both
                        relations.append((start_label, relation_label, end_label, edge))
                    else: 
                        if end_list[0].lower() == "a" or end_list[0].lower() == "an": # begins with article
                            relations.append((start_label, relation_label, ' '.join(end_list[1:]), edge))
                        else:
                            relations.append((start_label, relation_label, end_label, edge))
                            
                elif len(start_list) == 2 and (start_list[0] == "a" or start_list[0] == "an" or start_list[0] == "A"): # begins with article
                    if len(end_list) == 1:
                        relations.append((start_list[1], relation_label, end_label, edge))
                    else: 
                        if end_list[0].lower() == "a" or end_list[0].lower() == "an":
                            relations.append((start_list[1], relation_label, ' '.join(end_list[1:]), edge))
                        else: 
                            relations.append((start_list[1], relation_label, end_label, edge))
    return relations
            

def get_all_lemmas(concept):
    lemmas = concept.lemma_names()
    lemmas = [lemma.replace("_", " ") for lemma in lemmas]  
    lemmas = [lemma for lemma in lemmas if len(lemma.split()) == 1] # remove multiword lemmas
    lemmas = list(set(lemmas))
    return lemmas

def make_sentence_semagram(sentence, mask_token="[MASK]", trans_hyper = "is a"): 

    concept = sentence[0]
    slot = sentence[1]
    value = sentence[2]
    relation = sentence[3]

    correct_article = "An" if value[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "A"
    if relation == Slots.GENERALIZATION:
        if trans_hyper == "such as": 
            sentence_masked_concept = (f"{correct_article} {value}, {trans_hyper} the {mask_token}.", concept)
        elif trans_hyper == "is a": 
            sentence_masked_concept = (f"The {mask_token} is {correct_article.lower()} {value}.", concept)
        else: 
            sentence_masked_concept = (f"The {mask_token} {trans_hyper} {value}.", concept)
    else: 
        sentence_masked_concept = (f"The {mask_token} {slot} {value}.", concept)
    
    
    return sentence_masked_concept

def make_sentence_wn(concept1, relation, concept2, mask_token="[MASK]", trans_hyper = "is a"):

    sentence = None # masked first concept 
    correct_article = "An" if concept2[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "A"

    if relation == "hypernyms":
        
        if trans_hyper == "such as": 
            sentence = (f"{correct_article} {concept2}, {trans_hyper} the {mask_token}.", concept1)
        elif trans_hyper == "is a": 
            sentence = (f"The {mask_token} is {correct_article.lower()} {concept2}.", concept1)
        else: 
            sentence = (f"The {mask_token} {trans_hyper} {concept2}.", concept1)

                
    elif relation == "hyponyms":
        sentence = (f"The {mask_token} is a general term for {concept2}.", concept1)

    elif relation == "part_meronyms":
        sentence = (f"The {mask_token} have {correct_article.lower()} {concept2}.", concept1)
    
    
    return sentence
    
def make_sentence_cn(concept1, relation, concept2, mask_token="[MASK]", trans_hyper = "is a"):

    masked_first_concept = None
    correct_article_second_concept = "An" if concept2[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "A"
    
    if relation == "IsA":

        if trans_hyper == "such as": 
            masked_first_concept = (f"{correct_article_second_concept} {concept2}, {trans_hyper} the {mask_token}.", concept1)
        elif trans_hyper == "is a":
            masked_first_concept = (f"The {mask_token} is {correct_article_second_concept.lower()} {concept2}.", concept1)
        else: 
            masked_first_concept = (f"The {mask_token} {trans_hyper} {concept2}.", concept1)

    elif relation == "PartOf":
        masked_first_concept = (f"The {mask_token} is a part of {concept2}.", concept1)
    elif relation == "UsedFor":
        masked_first_concept = (f"The {mask_token} is used for {concept2}.", concept1)
    elif relation == "AtLocation": 
        masked_first_concept = (f"The {mask_token} is a typical location for {concept2}.", concept1)
    elif relation == "Synonym":
        masked_first_concept = (f"The {mask_token} is a synonym of {concept2}.", concept1)
    elif relation == "hyponym":
        masked_first_concept = (f"The {mask_token} is a general term for {concept2}.", concept1)

    return masked_first_concept 

def make_sentences_semagram(semagrams): 

    sentences_masked_hyper = []
    sentences_masked_hypo = []
    sentences_masked_part = []
    sentences_masked_material = []
    sentences_masked_behavior = []
    sentences_masked_size = []
    sentences_masked_efficiency = []
    sentences_masked_taste = []
    sentences_masked_shape = []
    sentences_masked_color_pattern = []
    sentences_masked_activity = []
    sentences_masked_consistency = []
    sentences_masked_how_to_use = []
    sentences_masked_purpose = []
    sentences_masked_content = []
    sentences_masked_product = []
    sentences_masked_supply = []
    sentences_masked_movement = []
    sentences_masked_time = []

    for semagram in semagrams:
        sentence_masked_concept = make_sentence_semagram(semagram, "[MASK]", 'is a specific term for')
        if semagram[3] == Slots.GENERALIZATION:
            sentences_masked_hyper.append(sentence_masked_concept) 
        elif semagram[3] == Slots.SPECIALIZATION: 
            sentences_masked_hypo.append(sentence_masked_concept)
        elif semagram[3] == Slots.PART: 
            sentences_masked_part.append(sentence_masked_concept)
        elif semagram[3] == Slots.MATERIAL: 
            sentences_masked_material.append(sentence_masked_concept)
        elif semagram[3] == Slots.BEHAVIOR: 
            sentences_masked_behavior.append(sentence_masked_concept)
        elif semagram[3] == Slots.SIZE:
            sentences_masked_size.append(sentence_masked_concept)
        elif semagram[3] == Slots.EFFICIENCY:
            sentences_masked_efficiency.append(sentence_masked_concept)
        elif semagram[3] == Slots.TASTE:
            sentences_masked_taste.append(sentence_masked_concept)
        elif semagram[3] == Slots.SHAPE:
            sentences_masked_shape.append(sentence_masked_concept)
        elif semagram[3] == Slots.COLOR_PATTERN:
            sentences_masked_color_pattern.append(sentence_masked_concept)
        elif semagram[3] == Slots.ACTIVITY:
            sentences_masked_activity.append(sentence_masked_concept)
        elif semagram[3] == Slots.CONSISTENCY:
            sentences_masked_consistency.append(sentence_masked_concept)
        elif semagram[3] == Slots.HOW_TO_USE:
            sentences_masked_how_to_use.append(sentence_masked_concept)
        elif semagram[3] == Slots.PURPOSE:
            sentences_masked_purpose.append(sentence_masked_concept)
        elif semagram[3] == Slots.CONTENT:
            sentences_masked_content.append(sentence_masked_concept)
        elif semagram[3] == Slots.PRODUCT: 
            sentences_masked_product.append(sentence_masked_concept)
        elif semagram[3] == Slots.SUPPLY:
            sentences_masked_supply.append(sentence_masked_concept)
        elif semagram[3] == Slots.MOVEMENT:
            sentences_masked_movement.append(sentence_masked_concept)
        elif semagram[3] == Slots.TIME:
            sentences_masked_time.append(sentence_masked_concept)

    return sentences_masked_hyper, sentences_masked_hypo, sentences_masked_part, sentences_masked_material, sentences_masked_behavior, sentences_masked_size, sentences_masked_efficiency, sentences_masked_taste, sentences_masked_shape, sentences_masked_color_pattern, sentences_masked_activity, sentences_masked_consistency, sentences_masked_how_to_use, sentences_masked_purpose, sentences_masked_content, sentences_masked_product, sentences_masked_supply, sentences_masked_movement, sentences_masked_time

def make_sentences_wn(relations):
    hypernym_sents_masked_first = []
    hyponym_sents_masked_first = []
    part_meronym_sents_masked_first = []
    
    for relation in relations:
        if len(relation[2]) > 0:
            masked_first_concepts = make_sentence_wn(relation[0], relation[1], relation[2], "[MASK]", "is a")
            if masked_first_concepts != None :
                if relation[1] == "hypernyms":
                    already_in = [(sentence, list) for sentence, list in hypernym_sents_masked_first if sentence == masked_first_concepts[0] and list == masked_first_concepts[1]]
                    if len(already_in) == 0:
                        hypernym_sents_masked_first.append(masked_first_concepts)
                elif relation[1] == "hyponyms":
                    already_in = [(sentence, list) for sentence, list in hyponym_sents_masked_first if sentence == masked_first_concepts[0] and list == masked_first_concepts[1]]
                    if len(already_in) == 0:
                        hyponym_sents_masked_first.append(masked_first_concepts)
                elif relation[1] == "part_meronyms":
                    already_in = [(sentence, list) for sentence, list in part_meronym_sents_masked_first if sentence == masked_first_concepts[0] and list == masked_first_concepts[1]]
                    if len(already_in) == 0:
                        part_meronym_sents_masked_first.append(masked_first_concepts)
    
    return hypernym_sents_masked_first, hyponym_sents_masked_first, part_meronym_sents_masked_first

def make_sentences_cn(relations):
    masked_first_concepts_hyper = []
    masked_first_concepts_hypo = []
    masked_first_concepts_part_of = []
    masked_first_concepts_used_for = []
    masked_first_concepts_at_location = []
    masked_first_concepts_synonym = []

    for relation in relations:
        masked_first_concept = make_sentence_cn(relation[0], relation[1], relation[2], "[MASK]", "such as") # TODO: SE VUOI CAMBIARE TRADUZIONE DI HYPER!
        
        if masked_first_concept != None:
            if relation[1] == "IsA":
                already_in = [(sentence, list) for sentence, list in masked_first_concepts_hyper if sentence == masked_first_concept[0] and list == masked_first_concept[1]]
                if len(already_in) == 0:
                    masked_first_concepts_hyper.append(masked_first_concept)
            
            elif relation[1] == "hyponym":
                already_in = [(sentence, list) for sentence, list in masked_first_concepts_hypo if sentence == masked_first_concept[0] and list == masked_first_concept[1]]
                if len(already_in) == 0:
                    masked_first_concepts_hypo.append(masked_first_concept)
            
            elif relation[1] == "PartOf":
                already_in = [(sentence, list) for sentence, list in masked_first_concepts_part_of if sentence == masked_first_concept[0] and list == masked_first_concept[1]]
                if len(already_in) == 0:
                    masked_first_concepts_part_of.append(masked_first_concept)

            elif relation[1] == "UsedFor": 
                already_in = [(sentence, list) for sentence, list in masked_first_concepts_used_for if sentence == masked_first_concept[0] and list == masked_first_concept[1]]
                if len(already_in) == 0:
                    masked_first_concepts_used_for.append(masked_first_concept)

            elif relation[1] == "AtLocation":
                already_in = [(sentence, list) for sentence, list in masked_first_concepts_at_location if sentence == masked_first_concept[0] and list == masked_first_concept[1]]
                if len(already_in) == 0:
                    masked_first_concepts_at_location.append(masked_first_concept)
            
            elif relation[1] == "Synonym":
                already_in = [(sentence, list) for sentence, list in masked_first_concepts_synonym if sentence == masked_first_concept[0] and list == masked_first_concept[1]]
                if len(already_in) == 0:
                    masked_first_concepts_synonym.append(masked_first_concept)
    
    return masked_first_concepts_hyper, masked_first_concepts_hypo, masked_first_concepts_part_of, masked_first_concepts_used_for, masked_first_concepts_at_location, masked_first_concepts_synonym    

def make_prompts_conceptnet():
    # prendo gli input che ho già per bert e li uso per fare i prompt

    path_sources = "it/unito/input/input_bert/cn/"

    directories_to_read = ["is_a/", "specific_term/", "such_as/"]

    further_analysis = []

    for directory in directories_to_read:
        masked_first_concepts_hyper = read_file_path(path_sources+directory, "masked_first_concept_hyper")
        masked_second_concepts_hyper = read_file_path(path_sources+directory, "masked_second_concept_hyper")
        further_analysis.append((directory, masked_first_concepts_hyper, masked_second_concepts_hyper))

   
    masked_first_concepts = read_file_path(path_sources, "masked_first_concept")
    masked_second_concepts = read_file_path(path_sources, "masked_second_concept")

    masked_first_concepts_prompt = create_prompt(masked_first_concepts)
    masked_second_concepts_prompt = create_prompt(masked_second_concepts)

    further_analysis_prompts = []

    for directory, masked_first_concepts_hyper, masked_second_concepts_hyper in further_analysis:
        masked_first_concepts_prompt_hyper = create_prompt(masked_first_concepts_hyper)
        masked_second_concepts_prompt_hyper = create_prompt(masked_second_concepts_hyper)
        further_analysis_prompts.append((directory, masked_first_concepts_prompt_hyper, masked_second_concepts_prompt_hyper))

    return masked_first_concepts_prompt, masked_second_concepts_prompt, further_analysis_prompts

def make_prompts_wordnet(): # TODO: cambia dato che ho eliminato alcune relazioni!!!!

    # prendo gli input che ho già per bert e li uso per fare i prompt

    path_sources = "it/unito/bert/input/input_bert/wn/"

    directories_to_read = ["is_a/", "specific_term/", "such_as/"]
    
    further_analysis = []
    for directory in directories_to_read:
        hypernym_sents_masked_first = read_file_path(path_sources+directory, "hypernym_sents_masked_first")
        hypernym_sents_masked_second = read_file_path(path_sources+directory, "hypernym_sents_masked_second")
        further_analysis.append((directory, hypernym_sents_masked_first, hypernym_sents_masked_second))

    hyponym_sents_masked_first = read_file_path(path_sources, "hyponym_sents_masked_first")
    hyponym_sents_masked_second = read_file_path(path_sources, "hyponym_sents_masked_second")
    member_holonym_sents = read_file_path(path_sources, "member_holonym_sents")
    part_meronym_sents = read_file_path(path_sources, "part_meronym_sents")
    substance_meronym_sents = read_file_path(path_sources, "substance_meronym_sents")

    
    hyponym_sents_masked_first_prompt = create_prompt(hyponym_sents_masked_first)
    hyponym_sents_masked_second_prompt = create_prompt(hyponym_sents_masked_second)
    member_holonym_sents_prompt = create_prompt(member_holonym_sents)
    part_meronym_sents_prompt = create_prompt(part_meronym_sents)
    substance_meronym_sents_prompt = create_prompt(substance_meronym_sents)

    further_analysis_prompts = []

    for directory, hypernym_sents_masked_first, hypernym_sents_masked_second in further_analysis:
        hypernym_sents_masked_first_prompt = create_prompt(hypernym_sents_masked_first)
        hypernym_sents_masked_second_prompt = create_prompt(hypernym_sents_masked_second)
        further_analysis_prompts.append((directory, hypernym_sents_masked_first_prompt, hypernym_sents_masked_second_prompt))

    
    return hyponym_sents_masked_first_prompt, hyponym_sents_masked_second_prompt, member_holonym_sents_prompt, part_meronym_sents_prompt, substance_meronym_sents_prompt, further_analysis_prompts
 
def create_prompt(sents):
    prompts = []
    for sent, exp in sents: 

        prompt = f"Provide a list of words that can replace \"[MASK]\" in the following sentence. \n\
Desired output: comma separated list of words. \n\
Sentence: \"{sent}\" \n\
Output:\n"
        prompts.append((prompt, exp))
    
    return prompts

def read_file_path(path, file):
    with open(path + file, "rb") as fp:
        return pickle.load(fp)

def merge_input_wordnet(sentences):
    dict_sentences = defaultdict(str)
    for sentence in sentences:
        if sentence[0] not in dict_sentences:
            dict_sentences[sentence[0]] = sentence[1]
        else: 
            for value_sentence in sentence[1]:
                if value_sentence not in dict_sentences[sentence[0]]:
                    dict_sentences[sentence[0]].append(value_sentence)

    return dict_sentences

def merge_input_without_list(sentences): 
    dict_sentences = defaultdict(str)
    for sentence in sentences:
        if sentence[0] not in dict_sentences:
            dict_sentences[sentence[0]] = [sentence[1]]
        else: 
            if sentence[1] not in dict_sentences[sentence[0]]:
                dict_sentences[sentence[0]].append(sentence[1])

    return dict_sentences

def check_preps(relations_cn):
    right_concept_preps = []
    right_preps = []
    for start_edge, rel, _, edge in relations_cn:
        if rel == "AtLocation": 
            text_example = edge["surfaceText"]
            if "in" in text_example:
                right_concept_preps.append((start_edge, "in"))
            elif "on" in text_example:
                right_concept_preps.append((start_edge, "on"))
            else: 
                right_concept_preps.append((start_edge, ""))
        else: 
            right_concept_preps.append(("No at location", ""))

    for start_edge, prep in right_concept_preps:
        if prep == "" and start_edge != "No at location":
            for start_edge2, prep2 in right_concept_preps:
                if start_edge == start_edge2 and prep2 != "":
                    right_preps.append(prep2)
                    break
        else: 
            right_preps.append(prep)
    
    return right_preps

if __name__ == '__main__':  

    resource = "semagram"
    directory = "input_bert"
    

    if directory == "input_phi-1.5":
        if resource == "conceptnet":
            masked_first_concept, masked_second_concept, further_analysis_prompts = make_prompts_conceptnet()

            # Save inputs

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_prompt", "wb") as fp:   #Pickling
                pickle.dump(masked_first_concept, fp)

            with open(f"it/unito/input/{directory}/cn/masked_second_concept_prompt", "wb") as fp:   #Pickling
                pickle.dump(masked_second_concept, fp)

            for inputs_further_analysis in further_analysis_prompts:
                with open(f"it/unito/input/{directory}/cn/{inputs_further_analysis[0]}masked_first_concept_hyper_prompt", "wb") as fp:   #Pickling
                    pickle.dump(inputs_further_analysis[1], fp)
                
                with open(f"it/unito/input/{directory}/cn/{inputs_further_analysis[0]}masked_second_concept_hyper_prompt", "wb") as fp:   #Pickling
                    pickle.dump(inputs_further_analysis[2], fp)

            #txt

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                for prompts in masked_first_concept:
                    fp.write(prompts[0] + " " + str(prompts[1]) + "\n\n")
            
            with open(f"it/unito/input/{directory}/cn/masked_second_concept_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                for prompts in masked_second_concept:
                    fp.write(prompts[0] + " " + str(prompts[1]) + "\n\n")
                
            for inputs_further_analysis in further_analysis_prompts:
                with open(f"it/unito/input/{directory}/cn/{inputs_further_analysis[0]}masked_first_concept_hyper_prompt.txt", "w", encoding="utf8") as fp:
                    for prompts in inputs_further_analysis[1]:
                        fp.write(prompts[0] + " " + str(prompts[1]) + "\n\n")

                with open(f"it/unito/input/{directory}/cn/{inputs_further_analysis[0]}masked_second_concept_hyper_prompt.txt", "w", encoding="utf8") as fp:
                    for prompts in inputs_further_analysis[2]:
                        fp.write(prompts[0] + " " + str(prompts[1]) + "\n\n")
            

        elif resource == "wordnet": # TODO: MODIFICA HO ELIMINATO RELAZIONI!!!
            hyponym_sents_masked_first, hyponym_sents_masked_second, member_holonym_sents, part_meronym_sents, substance_meronym_sents, further_analysis_prompts = make_prompts_wordnet()

            # Save inputs

            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_first_prompt", "wb") as fp:   #Pickling
                pickle.dump(hyponym_sents_masked_first, fp)
            
            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_second_prompt", "wb") as fp:   #Pickling
                pickle.dump(hyponym_sents_masked_second, fp)

            with open(f"it/unito/input/{directory}/wn/member_holonym_sents_prompt", "wb") as fp:   #Pickling
                pickle.dump(member_holonym_sents, fp)
            
            with open(f"it/unito/input/{directory}/wn/part_meronym_sents_prompt", "wb") as fp:   #Pickling
                pickle.dump(part_meronym_sents, fp)
            
            with open(f"it/unito/input/{directory}/wn/substance_meronym_sents_prompt", "wb") as fp:   #Pickling
                pickle.dump(substance_meronym_sents, fp)
            
            for inputs_further_analysis in further_analysis_prompts:
                with open(f"it/unito/input/{directory}/wn/{inputs_further_analysis[0]}hypernym_sents_masked_first_prompt", "wb") as fp:   #Pickling
                    pickle.dump(inputs_further_analysis[1], fp)
                
                with open(f"it/unito/input/{directory}/wn/{inputs_further_analysis[0]}hypernym_sents_masked_second_prompt", "wb") as fp:   #Pickling
                    pickle.dump(inputs_further_analysis[2], fp)

            #txt
            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_first_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                for sentence in hyponym_sents_masked_first:
                    fp.write(sentence[0] + " " + str(sentence[1]) + "\n\n")
            
            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_second_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                for sentence in hyponym_sents_masked_second:
                    fp.write(sentence[0] + " " + str(sentence[1]) + "\n\n")

            with open(f"it/unito/input/{directory}/wn/member_holonym_sents_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                for sentence in member_holonym_sents:
                    fp.write(sentence[0] + " " + str(sentence[1]) + "\n\n")
            
            with open(f"it/unito/input/{directory}/wn/part_meronym_sents_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                for sentence in part_meronym_sents:
                    fp.write(sentence[0] + " " + str(sentence[1]) + "\n\n")
            
            with open(f"it/unito/input/{directory}/wn/substance_meronym_sents_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                for sentence in substance_meronym_sents:
                    fp.write(sentence[0] + " " + str(sentence[1]) + "\n\n")
            
            
            for inputs_further_analysis in further_analysis_prompts:
                with open(f"it/unito/input/{directory}/wn/{inputs_further_analysis[0]}hypernym_sents_masked_first_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                    for prompts in inputs_further_analysis[1]:
                        fp.write(prompts[0] + " " + str(prompts[1]) + "\n\n")
                
                with open(f"it/unito/input/{directory}/wn/{inputs_further_analysis[0]}hypernym_sents_masked_second_prompt.txt", "w", encoding="utf8") as fp:   #Pickling
                    for prompts in inputs_further_analysis[2]:
                        fp.write(prompts[0] + " " + str(prompts[1]) + "\n\n")


    else: 
        # 1. get all concepts from semagram base
        concepts = get_all_concepts_obj()
        print(concepts.count_documents({}))
        if resource == "wordnet":
            # 2. search each concept on wordnet
            synsets = search_concepts_on_wordnet(concepts)
            #print(synsets)

            # 3. extract all relations that the concept has on wordnet
            relations = relations_on_wordnet(synsets)
            #print(relations)             
            
            # 4. make a sentence that exemplifies the relation with the concepts and masking

            hypernym_sents_masked_first, hyponym_sents_masked_first, part_meronym_sents_masked_first = make_sentences_wn(relations)
            print(len(hypernym_sents_masked_first))
            print(len(hyponym_sents_masked_first))
            print(len(part_meronym_sents_masked_first))

            
            hypernym_dict_sents = merge_input_wordnet(hypernym_sents_masked_first)
            hyponym_dict_sents = merge_input_wordnet(hyponym_sents_masked_first)
            part_meronym_dict_sents = merge_input_wordnet(part_meronym_sents_masked_first)

            # stamparlo e vedere il confronto tra il dizionario e il txt esteso!
            
            

            #5. Save sentences
            #binary

            with open(f"it/unito/input/{directory}/wn/hypernym_sents_masked_first", "wb") as fp:   #Pickling
                pickle.dump(list(hypernym_dict_sents.items()), fp)
            
            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_first", "wb") as fp:   #Pickling
                pickle.dump(list(hyponym_dict_sents.items()), fp)

            with open(f"it/unito/input/{directory}/wn/part_meronym_sents_masked_first", "wb") as fp:   #Pickling
                pickle.dump(list(part_meronym_dict_sents.items()), fp)

            # txt

            with open(f"it/unito/input/{directory}/wn/hypernym_sents_masked_first.txt", "w", encoding="utf8") as fp:
                for k, v in hypernym_dict_sents.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_first.txt", "w", encoding="utf8") as fp:
                for k, v in hyponym_dict_sents.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/wn/part_meronym_sents_masked_first.txt", "w", encoding="utf8") as fp:
                for k, v in part_meronym_dict_sents.items():
                    fp.write(f"{k} {v}\n")

                            

        elif resource == "conceptnet":

            # 2. search each concept on conceptnet

            concepts_cn = search_concepts_on_conceptnet(concepts)
            print("concept in conceptnet: ", len(concepts_cn))

            # 3. extract all relations that the concept has on conceptnet
            relations_cn = relations_on_conceptnet(concepts_cn)

            # 4. make a sentence that exemplifies the relation with the concepts and masking
            sentences_first_hyper, sentences_first_hypo, sentences_first_part_of, sentences_first_used_for, sentences_first_at_location, sentences_first_synonym  = make_sentences_cn(relations_cn)
            

            sentences_first_hyper_dict = merge_input_without_list(sentences_first_hyper)
            sentences_first_hypo_dict = merge_input_without_list(sentences_first_hypo)
            sentences_first_part_of_dict = merge_input_without_list(sentences_first_part_of)
            sentences_first_used_for_dict = merge_input_without_list(sentences_first_used_for)
            sentences_first_at_location_dict = merge_input_without_list(sentences_first_at_location)
            sentences_first_synonym_dict = merge_input_without_list(sentences_first_synonym)

            

            # 5. Save sentences 

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_hyper", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_first_hyper_dict.items()), fp)

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_hypo", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_first_hypo_dict.items()) , fp)

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_part_of", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_first_part_of_dict.items()) , fp)
            
            with open(f"it/unito/input/{directory}/cn/masked_first_concept_used_for", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_first_used_for_dict.items()), fp)

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_at_location", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_first_at_location_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/cn/masked_first_concept_synonym", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_first_synonym_dict.items()) , fp)

            # txt
                
            with open(f"it/unito/input/{directory}/cn/masked_first_concept_hyper.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_first_hyper_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_hypo.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_first_hypo_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_part_of.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_first_part_of_dict.items():
                    fp.write(f"{k} {v}\n")
                
            with open(f"it/unito/input/{directory}/cn/masked_first_concept_used_for.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_first_used_for_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/cn/masked_first_concept_at_location.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_first_at_location_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_synonym.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_first_synonym_dict.items():
                    fp.write(f"{k} {v}\n")
    

        elif resource == 'semagram':

            # in parts adesso c'è anche il tipo di relazione

            concepts_semagram = search_concepts_on_semagram()
            
            sentences_masked_hyper, sentences_masked_hypo, sentences_masked_part, sentences_masked_material, sentences_masked_behavior, sentences_masked_size, sentences_masked_efficiency, sentences_masked_taste, sentences_masked_shape, sentences_masked_color_pattern, sentences_masked_activity, sentences_masked_consistency, sentences_masked_how_to_use, sentences_masked_purpose, sentences_masked_content, sentences_masked_product, sentences_masked_supply, sentences_masked_movement, sentences_masked_time  = make_sentences_semagram(concepts_semagram)
            print(len(sentences_masked_hyper), "hypernyms", sentences_masked_hyper[0])
            print(len(sentences_masked_hypo), "hyponyms", sentences_masked_hypo[0])
            print(len(sentences_masked_part), "part", sentences_masked_part[0])
            print(len(sentences_masked_material), "material", sentences_masked_material[0])
            print(len(sentences_masked_behavior), "behavior",sentences_masked_behavior[0])
            print(len(sentences_masked_size), "size", sentences_masked_size[0])
            print(len(sentences_masked_efficiency), "efficiency", sentences_masked_efficiency[0])
            print(len(sentences_masked_taste), "taste", sentences_masked_taste[0])
            print(len(sentences_masked_shape), "shape", sentences_masked_shape[0])
            print(len(sentences_masked_color_pattern), "color pattern", sentences_masked_color_pattern[0])
            print(len(sentences_masked_activity), "activity", sentences_masked_activity[0])
            print(len(sentences_masked_consistency), "consistency", sentences_masked_consistency[0])
            print(len(sentences_masked_how_to_use), "how to use", sentences_masked_how_to_use[0])
            print(len(sentences_masked_purpose), "purpose", sentences_masked_purpose[0])
            print(len(sentences_masked_content), "content", sentences_masked_content[0])
            print(len(sentences_masked_product), "product", sentences_masked_product[0])
            print(len(sentences_masked_supply), "supply", sentences_masked_supply[0])
            print(len(sentences_masked_movement), "movement", sentences_masked_movement[0])
            print(len(sentences_masked_time), "time", sentences_masked_time[0])
            

            sentences_masked_hyper_dict = merge_input_without_list(sentences_masked_hyper)
            sentences_masked_hypo_dict = merge_input_without_list(sentences_masked_hypo)
            sentences_masked_part_dict = merge_input_without_list(sentences_masked_part)
            sentences_masked_material_dict = merge_input_without_list(sentences_masked_material)
            sentences_masked_behavior_dict = merge_input_without_list(sentences_masked_behavior)
            sentences_masked_size_dict = merge_input_without_list(sentences_masked_size)
            sentences_masked_efficiency_dict = merge_input_without_list(sentences_masked_efficiency)
            sentences_masked_taste_dict = merge_input_without_list(sentences_masked_taste)
            sentences_masked_shape_dict = merge_input_without_list(sentences_masked_shape)
            sentences_masked_color_pattern_dict = merge_input_without_list(sentences_masked_color_pattern)
            sentences_masked_activity_dict = merge_input_without_list(sentences_masked_activity)
            sentences_masked_consistency_dict = merge_input_without_list(sentences_masked_consistency)
            sentences_masked_how_to_use_dict = merge_input_without_list(sentences_masked_how_to_use)
            sentences_masked_purpose_dict = merge_input_without_list(sentences_masked_purpose)
            sentences_masked_content_dict = merge_input_without_list(sentences_masked_content)
            sentences_masked_product_dict = merge_input_without_list(sentences_masked_product)
            sentences_masked_supply_dict = merge_input_without_list(sentences_masked_supply)
            sentences_masked_movement_dict = merge_input_without_list(sentences_masked_movement)
            sentences_masked_time_dict = merge_input_without_list(sentences_masked_time)

            

            # Save sentences

            with open(f"it/unito/input/{directory}/semagram/masked_concept_hyper", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_hyper_dict.items()), fp)

            with open(f"it/unito/input/{directory}/semagram/masked_concept_hypo", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_hypo_dict.items()), fp)

            with open(f"it/unito/input/{directory}/semagram/masked_concept_part", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_part_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_material", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_material_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_behavior", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_behavior_dict.items()), fp)

            with open(f"it/unito/input/{directory}/semagram/masked_concept_size", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_size_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_efficiency", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_efficiency_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_taste", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_taste_dict.items()), fp)

            with open(f"it/unito/input/{directory}/semagram/masked_concept_shape", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_shape_dict.items()), fp)

            with open(f"it/unito/input/{directory}/semagram/masked_concept_color_pattern", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_color_pattern_dict.items()), fp)

            with open(f"it/unito/input/{directory}/semagram/masked_concept_activity", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_activity_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_consistency", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_consistency_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_how_to_use", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_how_to_use_dict.items()), fp)

            with open(f"it/unito/input/{directory}/semagram/masked_concept_purpose", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_purpose_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_content", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_content_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_product", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_product_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_supply", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_supply_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_movement", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_movement_dict.items()), fp)
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_time", "wb") as fp:   #Pickling
                pickle.dump(list(sentences_masked_time_dict.items()), fp)


            # txt
  
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_hyper.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_hyper_dict.items():
                    fp.write(f"{k} {v}\n") 

            with open(f"it/unito/input/{directory}/semagram/masked_concept_hypo.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_hypo_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/semagram/masked_concept_part.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_part_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_material.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_material_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_behavior.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_behavior_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_size.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_size_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_efficiency.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_efficiency_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_taste.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_taste_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_shape.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_shape_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_color_pattern.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_color_pattern_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/semagram/masked_concept_activity.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_activity_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/semagram/masked_concept_consistency.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_consistency_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/semagram/masked_concept_how_to_use.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_how_to_use_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/semagram/masked_concept_purpose.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_purpose_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_content.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_content_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/semagram/masked_concept_product.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_product_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_supply.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_supply_dict.items():
                    fp.write(f"{k} {v}\n")
            
            with open(f"it/unito/input/{directory}/semagram/masked_concept_movement.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_movement_dict.items():
                    fp.write(f"{k} {v}\n")

            with open(f"it/unito/input/{directory}/semagram/masked_concept_time.txt", "w", encoding="utf8") as fp:
                for k, v in sentences_masked_time_dict.items():
                    fp.write(f"{k} {v}\n")

            