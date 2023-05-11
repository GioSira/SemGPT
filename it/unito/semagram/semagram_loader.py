import xml.etree.ElementTree as ET
from it.unito.utils.utils import processValue

def __check(elem):
    return elem and (elem != 'none') and (elem != 'None') and (elem != '') and (elem != 'empty')

class Concept(object):

    def __init__(self, name, synset):
        self._name = name
        self._synset = synset
        self._slot_values = {}

    def get_values(self, slot):
        if slot not in self._slot_values:
            raise Exception(f"slot {slot} not in dict")

        return self._slot_values[slot]

    def transform_into_list(self, slot):
        l = []
        values = self.get_values(slot)
        for (v, p, synset) in values:
            l.append((slot, v, p, synset))

        return l

    def getAllSlots(self):
        l = set()
        for k in list(self._slot_values.keys()):
            for elem in self.transform_into_list(k):
                l.add(elem)

        return l

    def getName(self):
        return self._name

    def getSynset(self):
        return self._synset

    def insert(self, slot, value, pos, synset):

        self._slot_values.setdefault(slot, set())

        p = (value, pos, synset)
        self._slot_values[slot].add(p)


class Semagram(object):

    def __init__(self):

        self._concepts = {}

    def insertConcept(self, concept):
        self._concepts[concept.getName()] = concept


    def getConceptValues(self, c):

        if c not in self._concepts:
            raise Exception(f"concept {c} not in semagram base")

        concept = self._concepts[c]
        conceptSet = concept.getAllSlots()
        return conceptSet

    def getConceptsValues(self, list_of_concepts):

        tripletSet = set()
        for c in list_of_concepts:
            tripletSet.update(self.getConceptValues(c))

        return list(tripletSet)

    def getAllConcepts(self):
        return list(self._concepts.keys())


def read_xml(xml_file):

    semagram = Semagram()

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for c in root.findall("semagram"):

        concept_name = c.get("name")
        concept_synset = c.get("babelsynset")
        concept = Concept(concept_name, concept_synset)

        for slot in c.findall("slot"):
            slot_name = slot.get("name")

            for value in slot.findall("value"):
                value_synset = value.get("babelsynset")
                value_text = value.text

                for (s, v, p) in processValue(value_synset, value_text):
                    if __check(s) and __check(v) and __check(p):
                        concept.insert(slot_name, v, p, s)

        semagram.insertConcept(concept)

    return semagram
