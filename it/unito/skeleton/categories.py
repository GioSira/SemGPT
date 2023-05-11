from enum import Enum
from enum import auto


class Category(Enum):

    ANIMALS = auto()
    FOOD = auto()
    VEHICLES = auto()
    CLOTHES = auto()
    HOME = auto()
    APPLIANCE = auto()
    INSTRUMENTS = auto()
    ARTIFACTS = auto()
    TOOLS = auto()
    CONTAINERS = auto()


    @staticmethod
    def from_str(label):
        if label == 'animals':
            return Category.ANIMALS
        elif label == 'food':
            return Category.FOOD
        elif label == 'vehicles':
            return Category.VEHICLES
        elif label == 'clothes':
            return Category.CLOTHES
        elif label == 'home':
            return Category.HOME
        elif label == 'appliance':
            return Category.APPLIANCE
        elif label == 'instruments':
            return Category.INSTRUMENTS
        elif label == 'artifacts':
            return Category.ARTIFACTS
        elif label == 'tools':
            return Category.TOOLS
        elif label == 'containers':
            return Category.CONTAINERS
        else:
            raise Exception(f'category {label} not present')
