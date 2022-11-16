import re


def get_previous_generation_relationship(gender, direct_link, indirect_link, reciprocal_indirect_link=""):
    if direct_link == "father":
        if indirect_link == "":
            return "father", "son" if gender == "male" else "daughter"

        elif indirect_link == "spouse":
            return "mother", "son" if gender == "male" else "daughter"

        elif indirect_link == "son" or indirect_link == "daughter":
            return "brother" if indirect_link == "son" else "sister", "brother" if gender == "male" else "sister"

        elif indirect_link == "brother" or indirect_link == "sister":
            return "uncle" if indirect_link == "brother" else "aunt", "nephew" if gender == "male" else "neice"

        elif indirect_link == "nephew" or indirect_link == "neice":
            return "cousin", "cousin"

        elif indirect_link in ["father", "mother", "uncle"]:
            return f"grand-{indirect_link}", f"grand-{'son' if gender == 'male' else 'daughter'}"

        elif re.match(f".*grand.*", indirect_link):
            return f"great-{indirect_link}", f"great-{transformRelationGender(gender, reciprocal_indirect_link)}"

    elif direct_link == "spouse":
        if indirect_link == "":
            return "spouse", "spouse"

        return f"{indirect_link}-in-law", f"{transformRelationGender(gender, reciprocal_indirect_link)}-in-law"

    return None


def transformRelationGender(gender, relation):
    if gender == "male":
        relation = relation.replace("daughter", "son")
        relation = relation.replace("neice", "newphew")
        relation = relation.replace("aunt", "uncle")
        relation = relation.replace("sister", "brother")

    else:
        relation = relation.replace("son", "daughter")
        relation = relation.replace("newphew", "neice")
        relation = relation.replace("uncle", "aunt")
        relation = relation.replace("brother", "sister")

    return relation
