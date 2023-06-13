from it.unito.skeleton.categories import Category


def category2prompt(cat):

    if isinstance(cat, str):
        cat = Category.from_str(cat)

    assert isinstance(cat, Category), "input should be a category"

    if cat == Category.ANIMALS:
        return "animal"

    elif cat == Category.FOOD:
        return "food" # TODO: AGGIUNGERE DRINKS??

    elif cat == Category.VEHICLES:
        return "vehicle"

    elif cat == Category.CLOTHES:
        return "clothe"

    elif cat == Category.HOME: # home items???
        return "home item"

    elif cat == Category.APPLIANCE:
        return "appliance, equipment and device"

    elif cat == Category.INSTRUMENTS:
        return "music instrument"

    elif cat == Category.ARTIFACTS:
        return "object"

    elif cat == Category.TOOLS:
        return "tool"

    elif cat == Category.CONTAINERS:
        return "container"
    

def get_all_categories():
    return [c.name.lower() for c in Category]
