"""
This file is the actual fix for "the AI needs real context, not a made-up
grade_level string." Every concept ECHOFORGE can tag a mistake with maps
to a REAL, official Common Core State Standard — the same standard a
teacher would cite. Pulled from thecorestandards.org (the authoritative,
public-domain source) and verified by hand, not invented.

Why this matters: before this file existed, `sub_concept` was free text
someone typed into a form. Two mistakes about the exact same idea could
get labeled slightly differently and never connect. Now `concept_key` is
a fixed key into THIS dictionary — same key always means the same real
standard, every time.

Add a new concept by adding a new entry here. Don't invent a standard_code —
look up the real one at https://thecorestandards.org/Math/Content/ and copy
the real id + the real wording.
"""

CURRICULUM_STANDARDS: dict[str, dict] = {
    "fractions_subtract_same_whole": {
        "subject": "math",
        "standard_code": "CCSS.MATH.CONTENT.4.NF.B.3.D",
        "official_description": (
            "Solve word problems involving addition and subtraction of "
            "fractions referring to the same whole and having like "
            "denominators, e.g., by using visual fraction models and "
            "equations to represent the problem."
        ),
        "source_url": "https://thecorestandards.org/Math/Content/4/NF/B/3/d/",
    },
    "percent_of_a_quantity": {
        "subject": "math",
        "standard_code": "CCSS.MATH.CONTENT.6.RP.A.3.C",
        "official_description": (
            "Find a percent of a quantity as a rate per 100 (e.g., 30% of "
            "a quantity means 30/100 times the quantity); solve problems "
            "involving finding the whole, given a part and the percent."
        ),
        "source_url": "https://thecorestandards.org/Math/Content/6/RP/A/3/c/",
    },
    "unit_rate_constant_speed": {
        # Filed under "physics" in our app because that's the class the
        # mistake happened in — but notice the actual standard is a MATH
        # standard. That's not a bug. That's the whole point of ECHOFORGE:
        # the same underlying math idea shows up wearing a physics costume.
        "subject": "physics",
        "standard_code": "CCSS.MATH.CONTENT.6.RP.A.3.B",
        "official_description": (
            "Solve unit rate problems including those involving unit "
            "pricing and constant speed."
        ),
        "source_url": "https://thecorestandards.org/Math/Content/6/RP/A/3/b/",
    },
    "uniform_probability_model": {
        "subject": "math",
        "standard_code": "CCSS.MATH.CONTENT.7.SP.C.7.A",
        "official_description": (
            "Develop a uniform probability model by assigning equal "
            "probability to all outcomes, and use the model to determine "
            "probabilities of events."
        ),
        "source_url": "https://thecorestandards.org/Math/Content/7/SP/C/7/a/",
    },
}


def get_concept(concept_key: str) -> dict:
    try:
        return CURRICULUM_STANDARDS[concept_key]
    except KeyError as exc:
        valid = ", ".join(CURRICULUM_STANDARDS.keys())
        raise ValueError(
            f"Unknown concept_key '{concept_key}'. Must be one of: {valid}. "
            "Add new concepts to curriculum_standards.py, not as free text."
        ) from exc


def list_concepts() -> list[dict]:
    """Used by GET /api/concepts so the frontend dropdown stays in sync."""
    return [{"concept_key": key, **value} for key, value in CURRICULUM_STANDARDS.items()]
