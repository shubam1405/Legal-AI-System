import re
from database.vector_store import find_similar_cases


def get_similar_cases(text):

    results = find_similar_cases(text)

    docs = results["documents"][0]

    pattern = r"[A-Z][A-Za-z\s\.&]+ v\. [A-Z][A-Za-z\s\.&]+"

    cases = set()

    for doc in docs:

        matches = re.findall(pattern, doc)

        for m in matches:

            case = m.replace("\n", " ").strip()

            # remove trailing incomplete phrases
            case = case.replace(" and", "").strip()

            cases.add(case)

    return list(cases)