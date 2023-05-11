from it.unito.skeleton.slots import Slots
from it.unito.utils.utils import pluralize_word, conjugate_verb


def slot2prompt(slot, pos):

    if isinstance(slot, str):
        slot = Slots.from_str(slot)

    assert isinstance(slot, Slots), "input should be a slot"

    if slot in [Slots.PART, Slots.BODY_PART]:
        return "have"

    elif slot == Slots.ACTIVITY:
        return "can"

    elif slot == Slots.MATERIAL:
        return "are made of"

    elif slot in [Slots.COLOR_PATTERN, Slots.GENERALIZATION, Slots.SPECIALIZATION,
        Slots.CONSISTENCY, Slots.SIZE, Slots.SHAPE, Slots.EFFICIENCY,
        Slots.HOW_TO_USE, Slots.TASTE, Slots.SMELL, Slots.BEHAVIOUR]:
        return "are"

    elif slot == Slots.PURPOSE:

        if pos == "V":
            return "are used to"
        elif pos == "N":
            return "are used for"

    elif slot == Slots.USER:
        return "are used by"

    elif slot == Slots.GROUP:
        return "belong to"

    elif slot == Slots.CONTENT:
        return "contain"

    elif slot == Slots.PLACE:
        return "can be found in"

    elif slot == Slots.PRODUCT:
        return "are used for"

    elif slot == Slots.SUPPLY:
        return "use"

    elif slot == Slots.SOUND:

        if pos == "A":
            return "sound"

        elif pos in ["V", "N"]:
            return "can"

    elif slot == Slots.MOVEMENT:

        if pos in ["N", "V"]:
            return "can"

        elif pos == "A":
            return "are"

    elif slot == Slots.TIME:
        return "during"

    elif slot == Slots.ACCESSORY:
        return "are used with"


def value2prompt(value, slot):

    if isinstance(slot, str):
        slot = Slots.from_str(slot)

    assert isinstance(slot, Slots), f"slot {slot} does not belong to class Slots"

    if slot in [Slots.USER, Slots.PLACE, Slots.CONTENT]:
        return pluralize_word(value)
    elif slot in [Slots.HOW_TO_USE]:
        return conjugate_verb(value)
    else:
        return value
