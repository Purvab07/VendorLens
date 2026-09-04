from src.embed import get_collections, search
from src.reasoning import ask_model
from src.models import Flag, parse_model_response


def get_all_chunks(collection_name: str):
    collection = get_collections(collection_name)
    return collection.get()


def build_gap_prompt(regulation_text: str, vendor_text: str) -> str:
    return f"""Regulation requirement:
\"\"\"{regulation_text}\"\"\"

Vendor document excerpt (most relevant section found):
\"\"\"{vendor_text}\"\"\"

Question: Does the vendor document excerpt satisfy this regulation requirement?
Answer in this exact format:
VERDICT: <Satisfied / Gap Found / Unclear>
EXPLANATION: <one or two sentences, referencing the specific text that supports your verdict>
"""


def check_requirement(regulation_text: str, vendor_collection_name: str) -> Flag:
    match = search(query=regulation_text, collection_name=vendor_collection_name, n_results=1)
    vendor_text = match["documents"][0][0] if match["documents"][0] else "No relevant vendor text found."

    prompt = build_gap_prompt(regulation_text, vendor_text)
    response = ask_model(prompt)
    verdict, explanation = parse_model_response(response)

    return Flag(
        flag_type="gap",
        source_a="Regulation",
        text_a=regulation_text,
        source_b=vendor_collection_name,
        text_b=vendor_text,
        verdict=verdict,
        explanation=explanation,
        raw_response=response
    )


def run_gap_analysis(vendor_collection_name: str, regulation_collection_name: str = "regulations") -> list[Flag]:
    regulations = get_all_chunks(regulation_collection_name)
    results = []

    for reg_text in regulations["documents"]:
        result = check_requirement(reg_text, vendor_collection_name)
        results.append(result)

    return results


if __name__ == "__main__":
    findings = run_gap_analysis(vendor_collection_name="vendor_a")

    for i, flag in enumerate(findings, start=1):
        print(f"\n--- Requirement {i} ---")
        print(f"Regulation: {flag.text_a[:150]}...")
        print(f"Verdict: {flag.verdict}")
        print(f"Explanation: {flag.explanation}")