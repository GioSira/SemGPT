from enum import Enum
from enum import auto


class Slots(Enum):

    ACCESSORY = auto()
    ACTIVITY = auto()
    BEHAVIOR = auto()
    BODY_PART = auto()
    COLOR_PATTERN = auto()
    CONSISTENCY = auto()
    CONTENT = auto()
    EFFICIENCY = auto()
    GENERALIZATION = auto()
    GROUP = auto()
    HOW_TO_USE = auto()
    MATERIAL = auto()
    MOVEMENT = auto()
    PART = auto()
    PLACE = auto()
    PRODUCT = auto()
    PURPOSE = auto()
    SHAPE = auto()
    SIZE = auto()
    SMELL = auto()
    SOUND = auto()
    SPECIALIZATION = auto()
    SUPPLY = auto()
    TASTE = auto()
    TIME = auto()
    USER = auto()

    @staticmethod
    def from_str(label):

        if label == 'accessory':
            return Slots.ACCESSORY
        elif label == 'activity':
            return Slots.ACTIVITY
        elif label == 'behavior':
            return Slots.BEHAVIOR
        elif label == 'bodyPart':
            return Slots.BODY_PART
        elif label == 'colorPattern':
            return Slots.COLOR_PATTERN
        elif label == 'consistency':
            return Slots.CONSISTENCY
        elif label == 'content':
            return Slots.CONTENT
        elif label == 'efficiency':
            return Slots.EFFICIENCY
        elif label == 'generalization':
            return Slots.GENERALIZATION
        elif label == 'group':
            return Slots.GROUP
        elif label == 'howToUse':
            return Slots.HOW_TO_USE
        elif label == 'material':
            return Slots.MATERIAL
        elif label == 'movement':
            return Slots.MOVEMENT
        elif label == 'part':
            return Slots.PART
        elif label == 'place':
            return Slots.PLACE
        elif label == 'product':
            return Slots.PRODUCT
        elif label == 'purpose':
            return Slots.PURPOSE
        elif label == 'shape':
            return Slots.SHAPE
        elif label == 'size':
            return Slots.SIZE
        elif label == 'smell':
            return Slots.SMELL
        elif label == 'sound':
            return Slots.SOUND
        elif label == 'specialization':
            return Slots.SPECIALIZATION
        elif label == 'supply':
            return Slots.SUPPLY
        elif label == 'taste':
            return Slots.TASTE
        elif label == 'time':
            return Slots.TIME
        elif label == 'user':
            return Slots.USER
        else:
            raise Exception(f"slot {label} not in dict")
