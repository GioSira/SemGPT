import regex as re
from pathlib import Path
from glob import glob
import pickle
from nltk.stem import WordNetLemmatizer
from gensim.parsing.preprocessing import remove_stopword_tokens 


lemmatizer = WordNetLemmatizer()


def read_generated_concepts(concept_string):
    end_concept = get_end_concept(concept_string)
    words = [elem['token_str'] for elem in concept_string]
    #words = [x.lower().strip() for x in re.findall(r'[a-zA-Z ]+',concept_string)]
    #print("words: ", words)
    words = remove_stopword_tokens(words)
    words = [x for x in words if len(x) > 2 and x.isalpha()]
    #print("words senza stopwords e token no words: ", words)
    words = [lemmatizer.lemmatize(x.lower()) for x in words]
    #print("lemmatized: ", words)
    words = [x for x in words if x != end_concept]
    words = list(dict.fromkeys(words))
    #print("unique: ", words)
    return words

def get_end_concept(data):
    # per ottenere il concetto a cui è collegato il valore mascherato
    first_res = data[0]
    seq = first_res['sequence']
    connective = ' such as the '
    if ' such as the ' in seq:
        if 'A' == seq.split()[0]:
            return seq.split(', such as the')[0].replace('A ', '')
        else:
            return seq.split(', such as the')[0].replace('An ', '')
    elif ' can be used to ' in seq:
        connective = ' can be used to '
    elif ' can be made of ' in seq:
        connective = ' can be made of '
    elif ' can be used in the making of ' in seq:
        connective = ' can be used in the making of '
    elif ' can be eaten when ' in seq:
        connective = ' can be eaten when '
    elif ' can be ' in seq:
        connective = ' can be '
    elif ' can contain ' in seq:
        connective = ' can contain '
    elif ' can have a ' in seq:
        connective = ' can have a '
    elif ' can produce ' in seq:
        connective = ' can produce '
    elif ' can use ' in seq:
        connective = ' can use '
    elif ' can ' in seq:
        connective = ' can '
    elif ' is a general term for ' in seq:
        connective = ' is a general term for '
    elif ' is used for ' in seq:
        connective = ' is used for ' 
    elif ' are used for ' in seq:
        connective = ' are used for '
    elif ' are active during ' in seq: 
        connective = ' are active during '
    elif ' are ' in seq:
        connective = ' are '
    # FINO A QUI è PER SEMAGRAM
    elif ' is a part of ' in seq:
        connective = ' is a part of '
    elif ' is a typical location for ' in seq:
        connective = ' is a typical location for '
    elif ' is a synonym of ' in seq:
        connective = ' is a synonym of '
    # FINO A QUI è PER CN
    elif ' have an ' in seq:
        connective = ' have an '
    elif ' have a ' in seq:
        connective = ' have a '
    # FINO A QUI è PER WN
    
    return seq.split(connective)[-1].strip('.').strip() #TODO: controllare se è corretto!!

def read_generated_concepts_prompt(concept_string): # TODO: DA ELIMINARE!!!!

    #print("res: ", concept_string)
    concept_string = concept_string.split("Output:")[1]
    concept_string = concept_string.strip().split("\n")[0]
    #print("split: ", concept_string)
    words = [x.lower().strip() for x in re.findall(r'[a-zA-Z ]+',concept_string)]
    words = [x for x in words if x]
    #print("words: ", words)
    return words

  
def precision_at_k(target_list, gold_list, k):


    total = []
    for elem in target_list:
        if elem in gold_list:
            total.append(elem)
        
    target_list_k = target_list[:k]
    found = []
    for elem in target_list_k:
        if elem in gold_list:
            found.append(elem)

    inters = len(set(found).intersection(set(total)))
    
    # num_found -> relevant item

    if inters == 0 or len(found) == 0:
        return 0


    return inters / len(found)


def hits_at_k(target_list, gold_list, k):

    total = []
    for elem in target_list:
        if elem in gold_list:
            total.append(elem)
        
    target_list_k = target_list[:k]
    found = []
    for elem in target_list_k:
        if elem in gold_list:
            found.append(elem)

    inters = len(set(found).intersection(set(total)))

    if inters == 0 or len(total) == 0:
        return 0

    return inters/len(total)


def MRR(target_list, gold_list):

    index = 0
    for rank, elem in enumerate(target_list):
        if elem in gold_list:
            index = rank
            break

    if index == 0:
        return 0

    return 1. / index


def AP(target_list, gold_list, k):

    if k == 1:
        return precision_at_k(target_list, gold_list, 1)

    return precision_at_k(target_list, gold_list, k) + AP(target_list, gold_list, k-1)


def get_model_name(f_name):
    return Path(f_name).stem.split('__')[0].lower()


def compute_model_scores_k(model_name, model_file):

    p_1 = 0.
    p_2 = 0.
    p_5 = 0.
    p_10 = 0.

    h_1 = 0.
    h_2 = 0.
    h_5 = 0.
    h_10 = 0.

    ap_1 = 0.
    ap_2 = 0.
    ap_5 = 0.
    ap_10 = 0.

    map_1 = 0.
    map_2 = 0.
    map_5 = 0.
    map_10 = 0.

    mrr = 0.

    num_q = 0.

    with open(model_file, 'rb') as reader:
        output = pickle.load(reader)
        for data, concepts_eval in output:
            num_q += 1
            if model == 'phi-1.5':
                concepts = read_generated_concepts_prompt(data)
            else:
                concepts = read_generated_concepts(data)

            if len(concepts) > 0 and concepts_eval and len(concepts_eval) > 0:

                p_1 += precision_at_k(concepts, concepts_eval, 1)
                p_2 += precision_at_k(concepts, concepts_eval, 2)
                p_5 += precision_at_k(concepts, concepts_eval, 5)
                p_10 += precision_at_k(concepts, concepts_eval, 10)

                h_1 += hits_at_k(concepts, concepts_eval, 1)
                h_2 += hits_at_k(concepts, concepts_eval, 2)
                h_5 += hits_at_k(concepts, concepts_eval, 5)
                h_10 += hits_at_k(concepts, concepts_eval, 10)

                ap_1 += AP(concepts, concepts_eval, 1)
                ap_2 += AP(concepts, concepts_eval, 2) / 2.
                ap_5 += AP(concepts, concepts_eval, 5) / 5.
                ap_10 += AP(concepts, concepts_eval, 10) / 10.

                mrr += MRR(concepts, concepts_eval)

    p_1 /= num_q
    p_2 /= num_q
    p_5 /= num_q
    p_10 /= num_q

    h_1 /= num_q
    h_2 /= num_q
    h_5 /= num_q
    h_10 /= num_q

    map_1 = ap_1 / num_q
    map_2 = ap_2 / num_q
    map_5 = ap_5 / num_q
    map_10 = ap_10 / num_q

    mrr /= num_q
    model_file = model_file.split('/')[-1].split('.')[0]
    with open(f'it/unito/evaluation/{model_name}/{model_file}.txt', 'x', encoding="utf8") as writer:
        writer.write(f'P@1: {p_1}\n')
        writer.write(f'P@2: {p_2}\n')
        writer.write(f'P@5: {p_5}\n')
        writer.write(f'P@10: {p_10}\n')
        writer.write('\n============================\n')
        writer.write(f'H@1: {h_1}\n')
        writer.write(f'H@2: {h_2}\n')
        writer.write(f'H@5: {h_5}\n')
        writer.write(f'H@10: {h_10}\n')
        writer.write('\n============================\n')
        writer.write(f'MAP@1: {map_1}\n')
        writer.write(f'MAP@2: {map_2}\n')
        writer.write(f'MAP@5: {map_5}\n')
        writer.write(f'MAP@10: {map_10}\n')
        writer.write('\n============================\n')
        writer.write(f'MRR: {mrr}\n')

def compute_model_scores(model_name, model_file):
    p_1 = 0.
    p_2 = 0.
    p_5 = 0.
    p_10 = 0.

    h_1 = 0.
    h_2 = 0.
    h_5 = 0.
    h_10 = 0.

    ap_1 = 0.
    ap_2 = 0.
    ap_5 = 0.
    ap_10 = 0.

    map_1 = 0.
    map_2 = 0.
    map_5 = 0.
    map_10 = 0.

    mrr = 0.

    num_q = 0.

    with open(model_file, 'rb') as reader:
        output = pickle.load(reader)
        for data, concepts_eval in output:
            num_q += 1
            if model == 'phi-1.5':
                concepts = read_generated_concepts_prompt(data)
            else:
                concepts = read_generated_concepts(data)
            
            concepts_eval = [concepts_eval]

            if len(concepts) > 0 and concepts_eval and len(concepts_eval) > 0:

                p_1 += precision_at_k(concepts, concepts_eval, 1)
                p_2 += precision_at_k(concepts, concepts_eval, 2)
                p_5 += precision_at_k(concepts, concepts_eval, 5)
                p_10 += precision_at_k(concepts, concepts_eval, 10)

                h_1 += hits_at_k(concepts, concepts_eval, 1)
                h_2 += hits_at_k(concepts, concepts_eval, 2)
                h_5 += hits_at_k(concepts, concepts_eval, 5)
                h_10 += hits_at_k(concepts, concepts_eval, 10)

                ap_1 += AP(concepts, concepts_eval, 1)
                ap_2 += AP(concepts, concepts_eval, 2) / 2.
                ap_5 += AP(concepts, concepts_eval, 5) / 5.
                ap_10 += AP(concepts, concepts_eval, 10) / 10.

                mrr += MRR(concepts, concepts_eval)

    p_1 /= num_q
    p_2 /= num_q
    p_5 /= num_q
    p_10 /= num_q

    h_1 /= num_q
    h_2 /= num_q
    h_5 /= num_q
    h_10 /= num_q

    map_1 = ap_1 / num_q
    map_2 = ap_2 / num_q
    map_5 = ap_5 / num_q
    map_10 = ap_10 / num_q

    mrr /= num_q
    model_file = model_file.split('/')[-1].split('.')[0]
    with open(f'it/unito/evaluation/{model_name}/{model_file}.txt', 'x', encoding="utf8") as writer:
        writer.write(f'P@1: {p_1}\n')
        writer.write(f'P@2: {p_2}\n')
        writer.write(f'P@5: {p_5}\n')
        writer.write(f'P@10: {p_10}\n')
        writer.write('\n============================\n')
        writer.write(f'H@1: {h_1}\n')
        writer.write(f'H@2: {h_2}\n')
        writer.write(f'H@5: {h_5}\n')
        writer.write(f'H@10: {h_10}\n')
        writer.write('\n============================\n')
        writer.write(f'MAP@1: {map_1}\n')
        writer.write(f'MAP@2: {map_2}\n')
        writer.write(f'MAP@5: {map_5}\n')
        writer.write(f'MAP@10: {map_10}\n')
        writer.write('\n============================\n')
        writer.write(f'MRR: {mrr}\n')


def read_model_files_and_write_results(folder, model_name):

    for file in glob(folder+'/**/*.bin', recursive=True):
        
        print(f'File: {file}')
        compute_model_scores_k(model_name, file)


if __name__ == '__main__':

    model = "bert"
    kb = "wn"
    
    main_folder = f'/Users/128525/Desktop/Uni/SemGPT/it/unito/output/res_{model}/{kb}'

    read_model_files_and_write_results(main_folder, model)