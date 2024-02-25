from glob import glob
import pickle
import json
import random
from it.unito.eval_measures import read_generated_concepts

def generate_ds(results_hypo, results_hyper, results_other):
    ## Inserire tutti i risultati ottenuti 
    ds = []
    # 30 output devono essere presi casualmente da iponimia + iperonimia
    print(f'len hypo: {len(results_hypo)}')
    print(f'len hyper: {len(results_hyper)}')
    print(f'len other: {len(results_other)}')
    choice_hypo = random.sample(results_hypo, k=15)
    choice_hyper = random.sample(results_hyper, k=15)
    # 70 casualmente dal resto delle relazioni
    choice_other = random.sample(results_other, k=70)

   
    ds.extend(choice_hypo)
    ds.extend(choice_hyper)
    ds.extend(choice_other)
   
    return ds

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


def create_list_objects(file, relation):
    begin_list_objects = []
    #relation = file.split('/')[-1].split('_')[-2]
    list_objects = []

    with open(file, 'rb') as reader:
        output = pickle.load(reader)
        for data, concepts_eval in output:
            concepts = read_generated_concepts(data)
            concepts = [concept for concept in concepts if concept not in concepts_eval] # rimuovo i concetti già presenti nella risorsa
            end_concept = get_end_concept(data)
            begin_list_objects.append((concepts, end_concept, relation))

    
    for concepts, end_concept, relation in begin_list_objects:
        for c in concepts:
            dict_res = {'concept': end_concept, 'llm_concept': c, 'relation': relation} # ricorda che è al contrario rispetto a quello di FEDE!!!
            list_objects.append(dict_res)

    return list_objects




def read_model_files_and_write_results(folder, kb):

    results_hypo, results_hyper, results_other = [], [], []
    for file in glob(folder+'/**/*.bin', recursive=True):
        
        print(f'File: {file}')
        # creare la lista con i concetti restituiti dal modello SENZA quelli già inclusi nella risorsa 
        # quindi utilizzo la lista di risultati veri che dovevo ottenere per togliere i concetti già presenti
        # e poi prendere i restanti per fare il dataset
        relation = file.split('/')[-1].split('\\')[-1]
        if kb == "semagram": 
            relation = relation.replace('masked_concept_', '') 
            relation = relation.replace('_20.bin', '')
            #relation = relation.replace('_', ' ')

        elif kb == "cn":
            relation = relation.replace('masked_first_concept_', '') 
            relation = relation.replace('_20.bin', '')
            #relation = relation.replace('_', ' ')
            
        else:
            relation = relation.replace('_sents_masked_first_20.bin', '')
            #relation = relation.replace('_', ' ')

        if 'hyper' in relation:
            relation = 'hypernym'
        elif 'hypo' in relation:
            relation = 'hyponym'

        
        if '\\is_a\\' in file or '\\specific_term\\' in file:
            continue

        if 'hyper' in file or 'hypernym' in file:
            results_hyper.extend(create_list_objects(file, relation))
        elif 'hypo' in file or 'hyponym' in file:
            results_hypo.extend(create_list_objects(file, relation))
        else:
            results_other.extend(create_list_objects(file, relation))

    ds = generate_ds(results_hypo, results_hyper, results_other)

    with open(f'{folder}/ds_{kb}.txt', 'w', encoding='utf-8') as f: 
        f.write(json.dumps(ds, ensure_ascii=False, indent=4))
    print(f'Dataset salvato in {folder}/ds.txt')

    print("len ds: ", len(ds))
        

if __name__ == '__main__':

    model = "bert"
    kb = "semagram"
    
    main_folder = f'/Users/128525/Desktop/Uni/SemGPT/it/unito/output/res_{model}/{kb}'

    read_model_files_and_write_results(main_folder, kb)