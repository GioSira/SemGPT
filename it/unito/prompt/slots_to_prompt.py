from it.unito.skeleton.slots import Slots
from it.unito.skeleton.categories import Category
from it.unito.utils.utils import pluralize_word, conjugate_verb


def slot2prompt(slot, pos, category=None):

    if isinstance(slot, str):
        slot = Slots.from_str(slot)

    assert isinstance(slot, Slots), "input should be a slot"

    if slot == Slots.PART:
        return "can have"
    
    elif slot == Slots.BODY_PART: 
        return "can have or be used with"

    elif slot == Slots.MATERIAL:
        return "can be made of"

    elif slot in [Slots.GENERALIZATION, Slots.SPECIALIZATION]:
        return "are"
    
    elif slot in [Slots.BEHAVIOR, Slots.SIZE, Slots.EFFICIENCY, Slots.TASTE, Slots.SHAPE, Slots.COLOR_PATTERN, Slots.ACTIVITY, Slots.CONSISTENCY]: 
        return "can be"

    #TODO: shape potrebbe essere tradotto come "are SHAPE"/"have a SHAPE shape"

    #TODO: size potrebbe essere tradotto come "are SIZE size"
    
    elif slot == Slots.SMELL:
        return "can smell"
    
    elif slot == Slots.HOW_TO_USE:
        if pos == "V" or pos == "N":
            return "can be used for"
        elif pos == "A":
            return "can be used when"

    elif slot == Slots.PURPOSE:
        if pos == "V":
            return "are used to"
        elif pos == "N" or pos == "A": # nel caso di aggettivo potrebbe essere "[VALUE] purpose"
            return "are used for"

    elif slot == Slots.USER:
        return "are used by"

    elif slot == Slots.GROUP:
        return "groups into"

    elif slot == Slots.CONTENT:
        return "contain"

    elif slot == Slots.PLACE:
        return "can be found or used in"

    elif slot == Slots.PRODUCT: 
        return "can produce"

    elif slot == Slots.SUPPLY:
        return "use"

    elif slot == Slots.SOUND:
        if pos == "A":
            return "sound"
        elif pos in "N":
            return "can"
        elif pos == "V":
            return ""

    elif slot == Slots.MOVEMENT:
        if pos in ["N", "V"]:
            return "can"
        elif pos == "A":
            return "are"

    elif slot == Slots.TIME and category == "animals":
        return "are active during" 
    
    elif slot == Slots.TIME:
        return "can be consumed or used during"

    elif slot == Slots.ACCESSORY: 
        return "are related with"

def slot2promptEasy(slot, pos, category=None):
    if isinstance(slot, str):
        slot = Slots.from_str(slot)

    assert isinstance(slot, Slots), "input should be a slot"

    if slot == Slots.PART:
        return "can have a"
    
    #elif slot == Slots.BODY_PART: 
    #    return "can have or be used with"

    elif slot == Slots.MATERIAL:
        return "can be made of"

    elif slot == Slots.GENERALIZATION:
        return "is a"
    
    elif slot == Slots.SPECIALIZATION:
        return "is a general term for"
    
    elif slot in [Slots.BEHAVIOR, Slots.SIZE, Slots.EFFICIENCY, Slots.TASTE, Slots.SHAPE, Slots.COLOR_PATTERN, Slots.CONSISTENCY]: 
        return "can be"
    
    elif slot == Slots.ACTIVITY:
        return "can"
    
    #elif slot == Slots.SMELL: # can have a [VALUE] smell
    #    return "can have a smell"
    
    elif slot == Slots.HOW_TO_USE:
        if pos == "V" and category != "food":
            return "can be used to"
        elif pos == "A": #NB: sono solo 5 casi tutti di cibo!
            return "can be eaten when"
        #elif pos == 'N':
        #    return "can"

    elif slot == Slots.PURPOSE:
        if pos == "V":
            return "is used for"
        elif pos == "N" or pos == "A": # nel caso di aggettivo potrebbe essere "[VALUE] purpose"
            return "are used for"

    #elif slot == Slots.USER: #dipende dalla categoria!
    #    return "are used by"

    #elif slot == Slots.GROUP: ci sono alcune cose nosense tipo gli insetti si gruppano in "infestation"
    #    return "groups into"

    elif slot == Slots.CONTENT:
        return "can contain"

    #elif slot == Slots.PLACE: #dipende dalla categoria! ci sono animali/cibo che può essere tradotto con can be found oppure indumenti che invece è meglio tradurre in altro modo
    #    return "can be found or used in"

    elif slot == Slots.PRODUCT: 
        if category == "food":
            return "can be used in the making of"
        else:
            return "can produce"

    elif slot == Slots.SUPPLY:
        return "can use"

    #elif slot == Slots.SOUND:
    #    if pos == "A":
    #        return "sound"
    #    elif pos in "N":
    #        return "can"
    #    elif pos == "V":
    #        return ""

    elif slot == Slots.MOVEMENT:
        if pos in ["N", "V"]:
            return "can"
        elif pos == "A":
            return "are"

    elif slot == Slots.TIME and category == "animals":
        return "are active during" 
    
    #elif slot == Slots.TIME:
    #    return "can be consumed or used during"

    #elif slot == Slots.ACCESSORY: 
    #    return "are related with"


def value2prompt(value, slot):

    if isinstance(slot, str):
        slot = Slots.from_str(slot)

    assert isinstance(slot, Slots), f"slot {slot} does not belong to class Slots"

    if slot in [Slots.USER, Slots.PLACE, Slots.CONTENT]:
        return pluralize_word(value)
    else:
        return value
