"""Rule-based matcher: compares a user profile against each scheme's criteria dict."""

from schemes_data import SCHEMES


def find_matches(profile):
    matched = []
    for scheme in SCHEMES:
        if _is_eligible(profile, scheme["criteria"]):
            matched.append(scheme)
    return matched


def _is_eligible(profile, c):
    age = profile["age"]

    if c.get("min_age") is not None and age < c["min_age"]:
        return False
    if c.get("max_age") is not None and age > c["max_age"]:
        return False

    if c.get("gender") and profile["gender"] != c["gender"]:
        return False

    if c.get("max_income") is not None and profile["annual_income"] > c["max_income"]:
        return False

    if c.get("occupations") and profile["occupation"] not in c["occupations"]:
        return False

    categories = c.get("categories")
    gender_or_category = c.get("gender_or_category")
    if categories:
        category_ok = profile["social_category"] in categories
        gender_ok = gender_or_category and profile["gender"] == gender_or_category
        if not (category_ok or gender_ok):
            return False

    if c.get("requires_bpl") and not profile["is_bpl"]:
        return False

    if c.get("requires_disabled") and not profile["is_disabled"]:
        return False

    if c.get("requires_student") and not profile["is_student"]:
        return False

    if c.get("requires_widow") and not profile["is_widow"]:
        return False

    if c.get("requires_senior") and age < 60:
        return False

    if c.get("requires_daughter_under_10") and not profile["has_daughter_under_10"]:
        return False

    if c.get("requires_business_owner") and not profile["is_business_owner"]:
        return False

    if c.get("requires_no_house") and profile["owns_pucca_house"]:
        return False

    states_type = c.get("states_type")
    if states_type == "urban" and profile["area_type"] != "urban":
        return False
    if states_type == "rural" and profile["area_type"] != "rural":
        return False

    return True
