from it.unito.db.query_semagram import get_all_concepts
from nltk.corpus import wordnet as wn
from it.unito.bert.bert_models import get_model


def search_concepts_on_wordnet(concepts):
    synsets = []
    for concept in concepts:
        synsets.append(wn.synsets(concept))
    return synsets

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

def get_all_lemmas(concept):
    lemmas = concept.lemma_names()
    return lemmas

def make_sentence(concept1, relation, list_concept2):

    sentences_first_mask = []
    sentences_second_mask = []
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
            sentence1 = (f"{combination[0]} is an hypernym of [MASK].", combination[1])
            sentence2 = (f"[MASK] is an hypernym of {combination[1]}." , combination[0])
        elif relation == "hyponyms":
            sentence1 = (f"{combination[0]} is an hyponym of [MASK].", combination[1])
            sentence2 = (f"[MASK] is an hyponym of {combination[1]}.", combination[0])
        elif relation == "member_holonyms":
            sentence1 = (f"{combination[0]} have a part of [MASK].", combination[1])
            sentence2 = (f"[MASK] have a part of {combination[1]}.", combination[0])
        elif relation == "part_meronyms":
            sentence1 = (f"{combination[0]} is a part of [MASK]", combination[1])
            sentence2 = (f"[MASK] is a part of {combination[1]}", combination[0])
        elif relation == "substance_meronyms":
            sentence1 = (f"{combination[0]} is a part of [MASK]", combination[1])
            sentence2 = (f"[MASK] is a part of {combination[1]}", combination[0])
        elif relation == "entailments":
            sentence1 = (f"{combination[0]} involves [MASK]", combination[1])
            sentence2 = (f"[MASK] involves {combination[1]}", combination[0])
        
        sentences_first_mask.append(sentence1)
        sentences_second_mask.append(sentence2)
    
    return sentences_first_mask, sentences_second_mask
    
def make_sentences(relations):
    sentences_first = []
    sentences_second = []
    for relation in relations:
        if len(relation[2]) > 0:
            sentence_first, sentence_second = make_sentence(relation[0], relation[1], relation[2])
            sentences_first.extend(sentence_first)
            sentences_second.extend(sentence_second)
    
    return sentences_first, sentences_second

if __name__ == '__main__':

    # 1. get all concepts from semagram base
    concepts = get_all_concepts()
    #print(concepts)

    # 2. search each concept on wordnet
    synsets = search_concepts_on_wordnet(concepts)
    #print(synsets)

    # 3. extract all relations that the concept has on wordnet
    relations = relations_on_wordnet(synsets)
    #print(relations)

    # 4. make a sentence that exemplifies the relation with the concepts and masking
    
    sentences_first, sentences_second  = make_sentences(relations)
    print(sentences_first, sentences_second)

    # 5. get the output from bert and extract the masked word
    model = get_model()
    for sentence in sentences_first:
        print(model(sentence[0]))



