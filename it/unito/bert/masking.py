from it.unito.db.query_semagram import get_all_concepts_obj
from nltk.corpus import wordnet as wn
import warnings
warnings.simplefilter("ignore")
import requests
import pickle



def search_concepts_on_wordnet(concepts): # io ho il synset già da semagram, quindi non mi serve cercarlo
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
            relations.append((concept, "hypernyms", list(set([s for s in synset.closure(lambda s:s.hypernyms())]))))
            relations.append((concept, "hyponyms", list(set([s for s in synset.closure(lambda s: s.hyponyms())]))))

            # TODO: ULTERIORI STATISTICHE
            relations.append((concept, "member_holonyms", list(set(synset.member_holonyms()))))
            relations.append((concept, "member_meronyms", list(set(synset.member_meronyms()))))
            relations.append((concept, "part_holonyms", list(set(synset.part_holonyms()))))
            relations.append((concept, "part_meronyms", list(set(synset.part_meronyms()))))
            relations.append((concept, "substance_meronyms", list(set(synset.substance_meronyms()))))
            relations.append((concept, "substance_holonyms", list(set(synset.substance_holonyms()))))
            
        elif synset.pos() == 'v':
            relations.append((concept, "hypernyms", list(set(synset.closure(lambda s: s.hypernyms)))))
            
    return relations

def relations_on_conceptnet(concepts_cn):
    relations = []
    for concept_cn in concepts_cn:
        for edge in concept_cn["edges"]:
            if edge["rel"]["label"] != "ExternalURL" and edge["rel"]["label"] != "Entails" and \
                edge["rel"]["label"] != "InstanceOf" and edge["start"]["language"] == "en" and edge["end"]["language"] == "en":
                start_list = edge["start"]["label"].split()
                end_list = edge["end"]["label"].split()
                if len(start_list) == 1: 
                    if len(end_list) == 1: # one word for both
                        relations.append((edge["start"]["label"], edge["rel"]["label"], edge["end"]["label"]))
                    elif len(end_list) == 2 and (end_list[0] == "a" or end_list[0] == "an" or end_list[0] == "A"): # one word with article
                        relations.append((edge["start"]["label"], edge["rel"]["label"], end_list[1]))
                elif len(start_list) == 2 and (start_list[0] == "a" or start_list[0] == "an" or start_list[0] == "A"):
                    if len(end_list) == 1:
                        relations.append((start_list[1], edge["rel"]["label"], edge["end"]["label"]))
                    elif len(end_list) == 2 and (end_list[0] == "a" or end_list[0] == "an" or end_list[0] == "A"):
                        relations.append((start_list[1], edge["rel"]["label"], end_list[1]))
    return relations
            

def get_all_lemmas(concept):
    lemmas = concept.lemma_names()
    lemmas = [lemma.replace("_", " ") for lemma in lemmas]  
    lemmas = [lemma for lemma in lemmas if len(lemma.split()) == 1] # remove multiword lemmas
    lemmas = list(set(lemmas))
    return lemmas

def make_sentence_wn(concept1, relation, list_concept2, mask_token="[MASK]", trans_hyper = "is a"):

    masked_first_concept = []
    masked_second_concept = []
    words2 = []
    for concept2 in list_concept2:
        words2.extend(get_all_lemmas(concept2))
    
    words2 = list(set(words2)) # remove duplicates

    if words2 == []:
        return None, None

    sentence = None

    correct_article = "An" if concept1['concept'][0].lower() in ['a', 'e', 'i', 'o', 'u'] else "A"
    if relation == "hypernyms":

        # masked second concept 
        if trans_hyper == "such as": 
            sentence = (f"a {mask_token}, {trans_hyper} {correct_article.lower()} {concept1['concept']}.", words2)
        else: 
            sentence = (f"{correct_article} {concept1['concept']} {trans_hyper} {mask_token}.", words2)
        
        # masked first concept
        for synset in list_concept2: 
            
            hyponyms = list(set([s for s in synset.closure(lambda s:s.hyponyms())])) # TODO: forse mi è sufficiente la lemmatizzazione del synset di partenza

            lemmas_syn = get_all_lemmas(synset)
            if lemmas_syn == []:
                break
            lemma_hyponyms = []
            for hyponym in hyponyms:
                lemma_hyponyms.extend(get_all_lemmas(hyponym))

            lemma_hyponyms = list(set(lemma_hyponyms)) # remove duplicates

            if lemma_hyponyms == []:
                break
            for lemma in lemmas_syn:
                if trans_hyper == "such as": 
                    masked_first_concept.append((f"a {lemma}, {trans_hyper} {mask_token}.", lemma_hyponyms))
                else: 
                    masked_first_concept.append((f"The {mask_token} {trans_hyper} {lemma}.", lemma_hyponyms))
                
    elif relation == "hyponyms":
        sentence = (f"{correct_article} {concept1['concept']} is a general term for {mask_token}.", words2)
        for synset in list_concept2:
            hypernyms = synset.hypernyms()
            lemmas_syn = get_all_lemmas(synset)
            if lemmas_syn == []:
                break
            lemma_hypernyms = []
            for hypernym in hypernyms:
                lemma_hypernyms.extend(get_all_lemmas(hypernym))
            if lemma_hypernyms == []:
                break
            for lemma in lemmas_syn:
                masked_first_concept.append((f"The {mask_token} is a general term for {lemma}.", lemma_hypernyms))
    
    masked_second_concept.append(sentence)
    
    return masked_first_concept, masked_second_concept
    
def make_sentence_cn(concept1, relation, concept2, mask_token="[MASK]", trans_hyper = "is a"): # TODO: CAMBIA L'ARTICOLO NELL'INPUT!!

    masked_first_concept = None
    masked_second_concept = None

    if relation == "IsA":
        if trans_hyper == "such as": 
            masked_first_concept = (f"a {concept2}, {trans_hyper} {mask_token}.", concept1)
            masked_second_concept = (f"a {mask_token}, {trans_hyper} {concept1}.", concept2)
        else: 
            masked_second_concept = (f"{concept1} {trans_hyper} {mask_token}.", concept2)
            masked_first_concept = (f"The {mask_token} {trans_hyper} {concept2}.", concept1)
        
    elif relation == "HasA":
        masked_second_concept = (f"{concept1} belongs to {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} belongs to {concept2}.", concept1)
    elif relation == "PartOf":
        masked_second_concept = (f"{concept1} is a part of {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is a part of {concept2}.", concept1)
    elif relation == "RelatedTo":
        masked_second_concept = (f"{concept1} is related to {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is related to {concept2}.", concept1)
    elif relation == "FormOf":
        masked_second_concept = (f"{concept1} is a form of {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is a form of {concept2}.", concept1)
    elif relation == "UsedFor":
        masked_second_concept = (f"{concept1} is used for {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is used for {concept2}.", concept1)
    elif relation == "CapableOf":
        masked_second_concept = (f"{concept1} is capable of {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is capable of {concept2}.", concept1)
    elif relation == "AtLocation":
        masked_second_concept = (f"{concept1} is a typical location for {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is a typical location for {concept2}.", concept1)
    elif relation == "Causes":
        masked_second_concept = (f"{concept1} causes {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} causes {concept2}.", concept1)
    elif relation == "HasSubevent":
        masked_second_concept = (f"{concept1} has a subevent {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} has a subevent {concept2}.", concept1)
    elif relation == "HasFirstSubevent":
        masked_second_concept = (f"{concept1} is an event that begins with {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is an event that begins with {concept2}.", concept1)
    elif relation == "HasLastSubevent":
        masked_second_concept = (f"{concept1} is an event that ends with {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is an event that ends with {concept2}.", concept1)
    elif relation == "HasPrerequisite":
        masked_second_concept = (f"{concept1} is an event that requires {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is an event that requires {concept2}.", concept1)
    elif relation == "HasProperty":
        masked_second_concept = (f"{concept1} can be described as {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} can be described as {concept2}.", concept1)
    elif relation == "MotivatedByGoal":
        masked_second_concept = (f"{concept1} is an event that is motivated by the goal {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is an event that is motivated by the goal {concept2}.", concept1)
    elif relation == "ObstructedBy":
        masked_second_concept = (f"{concept1} is an event that is obstructed by {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is an event that is obstructed by {concept2}.", concept1)
    elif relation == "Desires":
        masked_second_concept = (f"{concept1} is an entity that tipically wants {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is an entity that tipically wants {concept2}.", concept1)
    elif relation == "CreatedBy":
        masked_second_concept = (f"{concept1} is created by {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is created by {concept2}.", concept1)
    elif relation == "Synonym":
        masked_second_concept = (f"{concept1} is a synonym of {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is a synonym of {concept2}.", concept1)
    elif relation == "Antonym": 
        masked_second_concept = (f"{concept1} is the opposite of {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is the opposite of {concept2}.", concept1)
    elif relation == "DistinctFrom":
        masked_second_concept = (f"{concept1} is distinct from {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is distinct from {concept2}.", concept1)
    elif relation == "DerivedFrom":
        masked_second_concept = (f"{concept1} is derived from {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is derived from {concept2}.", concept1)
    elif relation == "SymbolOf":
        masked_second_concept = (f"{concept1} symbolically represents {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} symbolically represents {concept2}.", concept1)
    elif relation == "DefinedAs":
        masked_second_concept = (f"{concept1} is defined as {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is defined as {concept2}.", concept1)
    elif relation == "MannerOf":
        masked_second_concept = (f"{concept1} is a specific way to do {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is a specific way to do {concept2}.", concept1)
    elif relation == "LocatedNear":
        masked_second_concept = (f"{concept1} is located near {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is located near {concept2}.", concept1)
    elif relation == "HasContext":
        masked_second_concept = (f"{concept1} is used in the context of {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is used in the context of {concept2}.", concept1)
    elif relation == "SimilarTo":
        masked_second_concept = (f"{concept1} is similar to {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is similar to {concept2}.", concept1)
    elif relation == "EtymologicallyRelatedTo":
        masked_second_concept = (f"{concept1} have a common origin with {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} have a common origin with {concept2}.", concept1)
    elif relation == "EtymologicallyDerivedFrom":
        masked_second_concept = (f"{concept1} is derived from {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is derived from {concept2}.", concept1)
    elif relation == "CausesDesire":
        masked_second_concept = (f"{concept1} makes someone want {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} makes someone want {concept2}.", concept1)
    elif relation == "MadeOf":
        masked_second_concept = (f"{concept1} is made of {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} is made of {concept2}.", concept1)
    elif relation == "ReceivesAction":
        masked_second_concept = (f"{concept1} can be done to {mask_token}.", concept2)
        masked_first_concept = (f"The {mask_token} can be done to {concept2}.", concept1)
    else:

        print("******************************************++relation not found ----- ", relation)
        print(concept1, concept2)

    return masked_first_concept, masked_second_concept


def make_sentences_wn(relations):
    #hypernym_sents_masked_first = []
    hypernym_sents_masked_second = []
    #hyponym_sents_masked_first = []
    hyponym_sents_masked_second = []
    
    for relation in relations:
        if len(relation[2]) > 0:
            masked_first_concepts, masked_second_concept = make_sentence_wn(relation[0], relation[1], relation[2], "<mask>", "such as") # TODO: se vuoi cambiare da is a ad altro qui!
            if masked_first_concepts != None and masked_second_concept != None:
                if relation[1] == "hypernyms":
                    #hypernym_sents_masked_first.extend(masked_first_concepts)
                    hypernym_sents_masked_second.extend(masked_second_concept)
                elif relation[1] == "hyponyms":
                    #hyponym_sents_masked_first.extend(masked_first_concepts)
                    hyponym_sents_masked_second.extend(masked_second_concept)
    
    return hypernym_sents_masked_second, hyponym_sents_masked_second

def make_sentences_cn(relations):
    masked_first_concepts = []
    masked_second_concepts = []
    masked_first_concepts_hyper = []
    masked_second_concepts_hyper = []
    for relation in relations:
        masked_first_concept, masked_second_concept = make_sentence_cn(relation[0], relation[1], relation[2], "<mask>", "such as") # TODO: SE VUOI CAMBIARE TRADUZIONE DI HYPER!
        
        if relation[1] == "IsA":
            masked_first_concepts_hyper.append(masked_first_concept)
            masked_second_concepts_hyper.append(masked_second_concept)
        else:
            masked_first_concepts.append(masked_first_concept)
            masked_second_concepts.append(masked_second_concept)
    
    return masked_first_concepts, masked_second_concepts, masked_first_concepts_hyper, masked_second_concepts_hyper

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


if __name__ == '__main__':  

    resource = "wordnet"
    directory = "input_roberta"
    

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

            hypernym_sents_masked_second, hyponym_sents_masked_second = make_sentences_wn(relations)
            print(len(hypernym_sents_masked_second))
            print(len(hyponym_sents_masked_second))

            #5. Save sentences
            #binary

            #with open(f"it/unito/input/{directory}/wn/hypernym_sents_masked_first", "wb") as fp:   #Pickling
            #    pickle.dump(hypernym_sents_masked_first, fp)

            with open(f"it/unito/input/{directory}/wn/hypernym_sents_masked_second", "wb") as fp:   #Pickling
                pickle.dump(hypernym_sents_masked_second, fp)

            #with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_first", "wb") as fp:   #Pickling
            #    pickle.dump(hyponym_sents_masked_first, fp)
            
            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_second", "wb") as fp:   #Pickling
                pickle.dump(hyponym_sents_masked_second, fp)
            

            # txt

            #with open(f"it/unito/input/{directory}/wn/hypernym_sents_masked_first.txt", "w", encoding="utf8") as fp:   
            #    for sentence in hypernym_sents_masked_first:
            #        fp.write(sentence[0] + " " + str(sentence[1]) + "\n")

            with open(f"it/unito/input/{directory}/wn/hypernym_sents_masked_second.txt", "w", encoding="utf8") as fp:
                for sentence in hypernym_sents_masked_second:
                    fp.write(sentence[0] + " " + str(sentence[1]) + "\n")
            
            #with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_first.txt", "w", encoding="utf8") as fp:
            #    for sentence in hyponym_sents_masked_first:
            #        fp.write(sentence[0] + " " + str(sentence[1]) + "\n")
            
            with open(f"it/unito/input/{directory}/wn/hyponym_sents_masked_second.txt", "w", encoding="utf8") as fp:
                for sentence in hyponym_sents_masked_second:
                    fp.write(sentence[0] + " " + str(sentence[1]) + "\n")
                            

        elif resource == "conceptnet":

            # 2. search each concept on conceptnet

            concepts_cn = search_concepts_on_conceptnet(concepts)
            print("concept in conceptnet: ", len(concepts_cn))

            # 3. extract all relations that the concept has on conceptnet
            relations_cn = relations_on_conceptnet(concepts_cn)

            # 4. make a sentence that exemplifies the relation with the concepts and masking
            sentences_first, sentences_second, sentences_first_hyper, sentences_second_hyper  = make_sentences_cn(relations_cn)
            
            # 5. Save sentences 
    
            with open(f"it/unito/input/{directory}/cn/masked_first_concept", "wb") as fp:   #Pickling
                pickle.dump(sentences_first, fp)

            with open(f"it/unito/input/{directory}/cn/masked_second_concept", "wb") as fp:   #Pickling
                pickle.dump(sentences_second, fp)

            with open(f"it/unito/input/{directory}/cn/masked_first_concept.txt", "w", encoding="utf8") as fp:
                for sentence in sentences_first:
                    fp.write(sentence[0] + " " + sentence[1] + "\n")

            with open(f"it/unito/input/{directory}/cn/masked_second_concept.txt", "w", encoding="utf8") as fp:
                for sentence in sentences_second:
                    fp.write(sentence[0] + " " + sentence[1] + "\n")


            with open(f"it/unito/input/{directory}/cn/masked_first_concept_hyper", "wb") as fp:   #Pickling
                pickle.dump(sentences_first_hyper, fp)

            with open(f"it/unito/input/{directory}/cn/masked_second_concept_hyper", "wb") as fp:   #Pickling
                pickle.dump(sentences_second_hyper, fp)

            with open(f"it/unito/input/{directory}/cn/masked_first_concept_hyper.txt", "w", encoding="utf8") as fp:
                for sentence in sentences_first_hyper:
                    fp.write(sentence[0] + " " + sentence[1] + "\n")

            with open(f"it/unito/input/{directory}/cn/masked_second_concept_hyper.txt", "w", encoding="utf8") as fp:
                for sentence in sentences_second_hyper:
                    fp.write(sentence[0] + " " + sentence[1] + "\n")
