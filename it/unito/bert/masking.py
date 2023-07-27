from it.unito.db.query_semagram import get_all_concepts
from nltk.corpus import wordnet as wn
from it.unito.bert.bert_models import get_model

import requests
import pickle


def search_concepts_on_wordnet(concepts):
    synsets = []
    for concept in concepts:
        synsets.append(wn.synsets(concept))
    return synsets

def search_concepts_on_conceptnet(concepts):
    concepts_cn = []
    for concept in concepts:
        concept_cn = requests.get(f"http://api.conceptnet.io/c/en/{concept}").json()
        print(concept_cn)
        concepts_cn.append(concept_cn)

    return concepts_cn

def relations_on_wordnet(synsets):
    relations = []
    for synsets_concept in synsets:
        for synset in synsets_concept:
            if synset.pos() == 'n':
                relations.append((synset, "hypernyms", synset.hypernyms()))
                relations.append((synset, "hyponyms", synset.hyponyms()))
                relations.append((synset, "member_holonyms", synset.member_holonyms()))
                relations.append((synset, "part_meronyms", synset.part_meronyms()))
                relations.append((synset, "substance_meronyms", synset.substance_meronyms()))
            elif synset.pos() == 'v':
                relations.append((synset, "entailments", synset.entailments()))
                relations.append((synset, "hypernyms", synset.hypernyms()))
            
    return relations

def relations_on_conceptnet(concepts_cn):
    relations = []
    for concept_cn in concepts_cn:
        for edge in concept_cn["edges"]:
            print(edge)
            if edge["rel"]["label"] != "ExternalURL" and edge["rel"]["label"] != "Entails" and \
                edge["rel"]["label"] != "InstanceOf" and edge["start"]["language"] == "en" and edge["end"]["language"] == "en":
                relations.append((edge["start"]["label"], edge["rel"]["label"], edge["end"]["label"]))
    return relations
            

def get_all_lemmas(concept):
    lemmas = concept.lemma_names()
    return lemmas

def make_sentence_wn(concept1, relation, list_concept2):

    masked_first_concept = []
    masked_second_concept = []
    words1 = get_all_lemmas(concept1)
    words2 = []
    for concept2 in list_concept2:
        words2.extend(get_all_lemmas(concept2))

    unique_combinations = []
 
    for i in range(len(words1)):
        for j in range(len(words2)):
            words1[i] = words1[i].replace("_", " ")
            words2[j] = words2[j].replace("_", " ")
            unique_combinations.append((words1[i], words2[j]))

    for combination in unique_combinations:
        sentence1 = None
        sentence2 = None
        if relation == "hypernyms":
            sentence2 = (f"{combination[0]} is an hypernym of [MASK].", combination[1])
            sentence1 = (f"The [MASK] is an hypernym of {combination[1]}." , combination[0])
        elif relation == "hyponyms":
            sentence2 = (f"{combination[0]} is an hyponym of [MASK].", combination[1])
            sentence1 = (f"The [MASK] is an hyponym of {combination[1]}.", combination[0])
        elif relation == "member_holonyms":
            sentence2 = (f"{combination[0]} have a part of [MASK].", combination[1])
            sentence1 = (f"The [MASK] have a part of {combination[1]}.", combination[0])
        elif relation == "part_meronyms":
            sentence2 = (f"{combination[0]} is a part of [MASK].", combination[1])
            sentence1 = (f"The [MASK] is a part of {combination[1]}", combination[0])
        elif relation == "substance_meronyms":
            sentence2 = (f"{combination[0]} is a part of [MASK].", combination[1])
            sentence1 = (f"The [MASK] is a part of {combination[1]}", combination[0])
        elif relation == "entailments":
            sentence2 = (f"{combination[0]} involves [MASK].", combination[1])
            sentence1 = (f"The [MASK] involves {combination[1]}", combination[0])
        
        masked_first_concept.append(sentence1)
        masked_second_concept.append(sentence2)
    
    return masked_first_concept, masked_second_concept
    
def make_sentence_cn(concept1, relation, concept2):

    masked_first_concept = None
    masked_second_concept = None

    if relation == "IsA":
        masked_second_concept = (f"{concept1} is a [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is a {concept2}.", concept1)
    elif relation == "HasA":
        masked_second_concept = (f"{concept1} belongs to [MASK].", concept2)
        masked_first_concept = (f"The [MASK] belongs to {concept2}.", concept1)
    elif relation == "PartOf":
        masked_second_concept = (f"{concept1} is a part of [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is a part of {concept2}.", concept1)
    elif relation == "RelatedTo":
        masked_second_concept = (f"{concept1} is related to [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is related to {concept2}.", concept1)
    elif relation == "FormOf":
        masked_second_concept = (f"{concept1} is a form of [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is a form of {concept2}.", concept1)
    elif relation == "UsedFor":
        masked_second_concept = (f"{concept1} is used for [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is used for {concept2}.", concept1)
    elif relation == "CapableOf":
        masked_second_concept = (f"{concept1} is capable of [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is capable of {concept2}.", concept1)
    elif relation == "AtLocation":
        masked_second_concept = (f"{concept1} is a typical location for [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is a typical location for {concept2}.", concept1)
    elif relation == "Causes":
        masked_second_concept = (f"{concept1} causes [MASK].", concept2)
        masked_first_concept = (f"The [MASK] causes {concept2}.", concept1)
    elif relation == "HasSubevent":
        masked_second_concept = (f"{concept1} has a subevent [MASK].", concept2)
        masked_first_concept = (f"The [MASK] has a subevent {concept2}.", concept1)
    elif relation == "HasFirstSubevent":
        masked_second_concept = (f"{concept1} is an event that begins with [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is an event that begins with {concept2}.", concept1)
    elif relation == "HasLastSubevent":
        masked_second_concept = (f"{concept1} is an event that ends with [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is an event that ends with {concept2}.", concept1)
    elif relation == "HasPrerequisite":
        masked_second_concept = (f"{concept1} is an event that requires [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is an event that requires {concept2}.", concept1)
    elif relation == "HasProperty":
        masked_second_concept = (f"{concept1} can be described as [MASK].", concept2)
        masked_first_concept = (f"The [MASK] can be described as {concept2}.", concept1)
    elif relation == "MotivatedByGoal":
        masked_second_concept = (f"{concept1} is an event that is motivated by the goal [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is an event that is motivated by the goal {concept2}.", concept1)
    elif relation == "ObstructedBy":
        masked_second_concept = (f"{concept1} is an event that is obstructed by [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is an event that is obstructed by {concept2}.", concept1)
    elif relation == "Desires":
        masked_second_concept = (f"{concept1} is an entity that tipically wants [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is an entity that tipically wants {concept2}.", concept1)
    elif relation == "CreatedBy":
        masked_second_concept = (f"{concept1} is created by [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is created by {concept2}.", concept1)
    elif relation == "Synonym":
        masked_second_concept = (f"{concept1} is a synonym of [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is a synonym of {concept2}.", concept1)
    elif relation == "Antonym": # TODO: forse dovrei scrivere opposto?????
        masked_second_concept = (f"{concept1} is the opposite of [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is the opposite of {concept2}.", concept1)
    elif relation == "DistinctFrom":
        masked_second_concept = (f"{concept1} is distinct from [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is distinct from {concept2}.", concept1)
    elif relation == "DerivedFrom":
        masked_second_concept = (f"{concept1} is derived from [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is derived from {concept2}.", concept1)
    elif relation == "SymbolOf":
        masked_second_concept = (f"{concept1} symbolically represents [MASK].", concept2)
        masked_first_concept = (f"The [MASK] symbolically represents {concept2}.", concept1)
    elif relation == "DefinedAs":
        masked_second_concept = (f"{concept1} is defined as [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is defined as {concept2}.", concept1)
    elif relation == "MannerOf":
        masked_second_concept = (f"{concept1} is a specific way to do [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is a specific way to do {concept2}.", concept1)
    elif relation == "LocatedNear":
        masked_second_concept = (f"{concept1} is located near [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is located near {concept2}.", concept1)
    elif relation == "HasContext":
        masked_second_concept = (f"{concept1} is used in the context of [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is used in the context of {concept2}.", concept1)
    elif relation == "SimilarTo":
        masked_second_concept = (f"{concept1} is similar to [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is similar to {concept2}.", concept1)
    elif relation == "EtymologicallyRelatedTo":
        masked_second_concept = (f"{concept1} have a common origin with [MASK].", concept2)
        masked_first_concept = (f"The [MASK] have a common origin with {concept2}.", concept1)
    elif relation == "EtymologicallyDerivedFrom":
        masked_second_concept = (f"{concept1} is derived from [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is derived from {concept2}.", concept1)
    elif relation == "CausesDesire":
        masked_second_concept = (f"{concept1} makes someone want [MASK].", concept2)
        masked_first_concept = (f"The [MASK] makes someone want {concept2}.", concept1)
    elif relation == "MadeOf":
        masked_second_concept = (f"{concept1} is made of [MASK].", concept2)
        masked_first_concept = (f"The [MASK] is made of {concept2}.", concept1)
    elif relation == "ReceivesAction":
        masked_second_concept = (f"{concept1} can be done to [MASK].", concept2)
        masked_first_concept = (f"The [MASK] can be done to {concept2}.", concept1)
    else:

        print("******************************************++relation not found ----- ", relation)
        print(concept1, concept2)

    return masked_first_concept, masked_second_concept


def make_sentences_wn(relations):
    masked_first_concepts = []
    masked_second_concepts = []
    for relation in relations:
        if len(relation[2]) > 0:
            masked_first_concept, masked_second_concept = make_sentence_wn(relation[0], relation[1], relation[2])
            masked_first_concepts.extend(masked_first_concept)
            masked_second_concepts.extend(masked_second_concept)
    
    return masked_first_concepts, masked_second_concepts

def make_sentences_cn(relations):
    masked_first_concepts = []
    masked_second_concepts = []
    for relation in relations:
        masked_first_concept, masked_second_concept = make_sentence_cn(relation[0], relation[1], relation[2])
        masked_first_concepts.append(masked_first_concept)
        masked_second_concepts.append(masked_second_concept)
    
    return masked_first_concepts, masked_second_concepts


if __name__ == '__main__':  

    resource = "conceptnet"
    # 1. get all concepts from semagram base
    concepts = get_all_concepts()
    #print(concepts)

    if resource == "wordnet":
        # 2. search each concept on wordnet
        synsets = search_concepts_on_wordnet(concepts)
        #print(synsets)

        # 3. extract all relations that the concept has on wordnet
        relations = relations_on_wordnet(synsets)
        #print(relations)

        # 4. make a sentence that exemplifies the relation with the concepts and masking
        
        sentences_masked_first, sentences_masked_second  = make_sentences_wn(relations)
        print(sentences_masked_first, sentences_masked_second)

        print(len(sentences_masked_first), len(sentences_masked_second))

        # 5. get the output from bert and extract the masked word
        #model = get_model()
        #for sentence in sentences_masked_first:
        #    print(model(sentence[0]))

        #6. Save sentences
        #binary
        #with open(f"it/unito/bert/input_bert/wn/masked_first_concept", "wb") as fp:   #Pickling
        #    pickle.dump(sentences_masked_first, fp)

        #with open(f"it/unito/bert/input_bert/wn/masked_second_concept", "wb") as fp:   #Pickling
        #    pickle.dump(sentences_masked_second, fp)

        # txt
        with open(f"it/unito/bert/input_bert/wn/masked_first_concept.txt", "w") as fp:
            for sentence in sentences_masked_first:
                fp.write(sentence[0] + " " + sentence[1] + "\n")

        with open(f"it/unito/bert/input_bert/wn/masked_second_concept.txt", "w") as fp:
            for sentence in sentences_masked_second:
                fp.write(sentence[0] + " " + sentence[1] + "\n")
                        

    elif resource == "conceptnet":

        # 2. search each concept on conceptnet

        concepts_cn = search_concepts_on_conceptnet(concepts)

        # 3. extract all relations that the concept has on conceptnet
        relations_cn = relations_on_conceptnet(concepts_cn)

        # 4. make a sentence that exemplifies the relation with the concepts and masking
        sentences_first, sentences_second  = make_sentences_cn(relations_cn)
        #print(sentences_first, sentences_second)

        #print(len(sentences_first), len(sentences_second))
        # 5. Save sentences 
 
        #with open(f"it/unito/bert/input_bert/cn/masked_first_concept", "wb") as fp:   #Pickling
        #    pickle.dump(sentences_first, fp)

        #with open(f"it/unito/bert/input_bert/cn/masked_second_concept", "wb") as fp:   #Pickling
        #    pickle.dump(sentences_second, fp)

        with open(f"it/unito/bert/input_bert/cn/masked_first_concept.txt", "w") as fp:
            for sentence in sentences_first:
                fp.write(sentence[0] + " " + sentence[1] + "\n")

        with open(f"it/unito/bert/input_bert/cn/masked_second_concept.txt", "w") as fp:
            for sentence in sentences_second:
                fp.write(sentence[0] + " " + sentence[1] + "\n")


        # 6. get the output from bert and extract the masked word
        #model = get_model()
        #for sentence in sentences_first:
        #    print(model(sentence))






