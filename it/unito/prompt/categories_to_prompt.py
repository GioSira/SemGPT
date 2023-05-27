from it.unito.skeleton.categories import Category


def category2prompt(cat):

    if isinstance(cat, str):
        cat = Category.from_str(cat)

    assert isinstance(cat, Category), "input should be a category"

    if cat == Category.ANIMALS:
        return "animals"

    elif cat == Category.FOOD:
        return "foods" # TODO: AGGIUNGERE DRINKS??

    elif cat == Category.VEHICLES:
        return "vehicles"

    elif cat == Category.CLOTHES:
        return "clothes"

    elif cat == Category.HOME:
        return "house furniture and kitchen utensils"

    elif cat == Category.APPLIANCE:
        return "appliances, equipments and devices"

    elif cat == Category.INSTRUMENTS:
        return "music instruments"

    elif cat == Category.ARTIFACTS:
        return "objects"

    elif cat == Category.TOOLS:
        return "tools"

    elif cat == Category.CONTAINERS:
        return "containers"
    

def get_all_categories():
    return [c.name.lower() for c in Category]
