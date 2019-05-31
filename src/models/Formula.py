class Formula:
    id = None
    name = None
    child_formulas = []
    category = None
    abbreviation = None
    parent_id = None
    has_children = None

    def __init__(self, id, name, category, abbreviation, parent_id, has_children):
        self.id = id
        self.name = name
        self.category = category
        self.abbreviation = abbreviation
        self.parent_id = parent_id
        self.has_children = has_children
