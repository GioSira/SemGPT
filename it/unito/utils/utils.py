from pattern.text import conjugate, pluralize


def pluralize_word(word):
    return pluralize(word, language="en")


def conjugate_verb(verb, progressive=False):
    if progressive:
        return conjugate(verb, tense="past", person=2, language="en", aspect="progressive")
    else:
        return conjugate(verb, tense="past", person=2, language="en")


def __clear_text(value):
    if '_' in value:
        return ' '.join(value.split('_'))
    else:
        return value


def __split_vp(value):

    if "#" in value:
        v, p = value.split('#')
        return [__clear_text(v), p]
    else:
        return [__clear_text(value), 'empty']


def __get_pos_from_synset(synset):
    if synset and (synset != '') and (synset != 'none') and (synset != 'empty'):
        return str.upper(synset[-1])
    else:
        return 'empty'


def processValue(synset, value):

    l = []

    if ',' in synset:
        synsets = synset.split(',')
        vp_s = __split_vp(value)
        value = vp_s[0]

        for s in synsets:
            l.append((s, value, __get_pos_from_synset(s)))

    elif ',' in value:
        vp_list = value.split(',')
        for vp in vp_list:
            v, p = __split_vp(vp)
            l.append((synset, v, __get_pos_from_synset(synset)))

    else:
        v, p = __split_vp(value)
        l.append((synset, v, __get_pos_from_synset(synset)))

    return l