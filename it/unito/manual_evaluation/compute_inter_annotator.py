import json

import numpy as np

#from read_files import read_all_data

import math
from statsmodels.stats.inter_rater import fleiss_kappa


def _map_value(v):

    if v == 'yes':
        return 1
    elif v == 'wrong':
        return -1
    else:
        return 0


def _majority_voting(vector):

    value_sum = sum(vector)
    min_t = math.ceil(len(vector) / 2)

    if value_sum < 0:
        return "wrong"
    elif value_sum >= min_t:
        return "correct"
    elif value_sum < min_t:
        return "incorrect"
    else:
        raise Exception(f'the sum is {value_sum}')


def get_label_vector(length, data):

    ann_array = [[] for _ in range(length)]
    for name in data.keys():
        for i, val in enumerate(data[name]['answers']):
            ann_array[i].append(_map_value(val))

    return ann_array


def get_ann_matrix(ann_vector):

    n = len(ann_vector)
    M = np.zeros((n, 3))

    for i, v in enumerate(ann_vector):
        for el in v:
            if el == 1:
                M[i, 0] += 1
            elif el == 0:
                M[i, 1] += 1
            else:
                M[i, 2] += 1

    return M


def _get_agreement(value):

    if value <= 0:
        return "Poor"
    elif 0 < value <= 0.2:
        return "Slight"
    elif 0.2 < value <= 0.4:
        return "Fair"
    elif 0.4 < value <= 0.6:
        return "Moderate"
    elif 0.6 < value <= 0.8:
        return "Substatial"
    elif value > 0.8:
        return "Almost perfect"
    else:
        raise Exception(f"score is {value}.")


def compute_iia(matrix):
    fleiss = fleiss_kappa(matrix)
    uniform = fleiss_kappa(matrix, method='uniform')
    print(f"Fleiss's kappa: {fleiss}: {_get_agreement(fleiss)}")
    print(f"Randolph's mulirated kappa: {uniform}: {_get_agreement(uniform)}")


def generate_annotated_file(fout, data, l_vec):

    name = list(data.keys())[0]
    concepts = data[name]['concept']
    llm_concept = data[name]['llm_concept']
    relation = data[name]['relation']
    #categories = data[name]['category']
    #criterias = data[name]['criterion']
    models = data[name]['models']

    triplets = list(zip(concepts, llm_concept, relation, models))

    with open(fout, 'w', encoding='utf-8') as writer:
        for i, (con, llm_concept, relation, model) in enumerate(triplets): #for i, (con, cat, cri, model) in enumerate(triplets):
            writer.write(
                f"{json.dumps({'concept': con, 'llm_concept': llm_concept, 'relation': relation, 'model': model, 'annotation': _majority_voting(l_vec[i])})}\n"
            )


if __name__ == '__main__':
    pass
    # TODO: riscrivere tutto per leggere i dati
    #index, d = read_all_data('../manual_evaluation/multialign_finale', debug=False)
    #l_vec = get_label_vector(index, d)
    #matrix = get_ann_matrix(l_vec)
    #compute_iia(matrix)
    #generate_annotated_file('../manual_evaluation/multialign_finale/multialign_finale_merge.jsonl', d, l_vec)