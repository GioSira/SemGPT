from it.unito.skeleton.slots import Slots
from it.unito.skeleton.categories import Category
from it.unito.utils.utils import pluralize_word, conjugate_verb


def slot2prompt(slot, pos, category=None):

    if isinstance(slot, str):
        slot = Slots.from_str(slot)

    assert isinstance(slot, Slots), "input should be a slot"

    if slot == Slots.PART:
        return "can have "
    
    elif slot == Slots.BODY_PART: 
        return "can have or be used with"

    elif slot == Slots.MATERIAL:
        return "can be made of"

    elif slot in [Slots.GENERALIZATION, Slots.SPECIALIZATION]:
        return "are"
    
    elif slot in [Slots.BEHAVIOR, Slots.SIZE, Slots.EFFICIENCY, Slots.TASTE, Slots.SHAPE, Slots.COLOR_PATTERN, Slots.ACTIVITY]: 
        return "can be"

    elif slot == Slots.SHAPE:
        return "can have a shape"

    elif slot == Slots.SMELL:
        return "can smell"

    elif slot == Slots.CONSISTENCY: 
        return "can have a consistency or taste"
    
    elif slot == Slots.HOW_TO_USE:

        if pos == "V" or pos == "N":
            return "can be or be used for"
        elif pos == "A":
            return "can be used when"

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
        return "can be found or used in"

    elif slot == Slots.PRODUCT:
        return "make or are made from"

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

    elif slot == Slots.TIME and category == "animals":
        return "live during"
    
    elif slot == Slots.TIME:
        return "can be consumed or used during"

    elif slot == Slots.ACCESSORY: 
        return "may have to do with"


def value2prompt(value, slot):

    if isinstance(slot, str):
        slot = Slots.from_str(slot)

    assert isinstance(slot, Slots), f"slot {slot} does not belong to class Slots"

    if slot in [Slots.USER, Slots.PLACE, Slots.CONTENT]:
        return pluralize_word(value)
    else:
        return value
