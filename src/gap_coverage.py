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

You are explaining this to someone with no legal or compliance background.
Answer in this exact format, with no extra text before or after:

TOPIC: <a short 2-4 word category for this requirement, e.g. "Complaint Timeline">
SEVERITY: <High / Medium / Low — how serious a problem this would be if unresolved>
VERDICT: <Satisfied / Gap Found / Unclear>
QUOTE_A: <copy the exact sentence from the regulation requirement that sets the rule — word for word, no paraphrasing>
QUOTE_B: <copy the exact sentence from the vendor excerpt that is most relevant, or write "No relevant sentence found" if nothing addresses it>
PLAIN_EXPLANATION: <1-2 sentences in simple, everyday language explaining what the rule requires, what the vendor actually commits to, and why that is or isn't good enough>
"""


def check_requirement(regulation_text: str, vendor_collection_name: str) -> Flag:
    match = search(query=regulation_text, collection_name=vendor_collection_name, n_results=1)
    vendor_text = match["documents"][0][0] if match["documents"][0] else "No relevant vendor text found."

    prompt = build_gap_prompt(regulation_text, vendor_text)
    response = ask_model(prompt)
    parsed = parse_model_response(response)

    return Flag(
        flag_type="gap",
        source_a="Regulation",
        text_a=regulation_text,
        source_b=vendor_collection_name,
        text_b=vendor_text,
        quote_a=parsed["quote_a"],
        quote_b=parsed["quote_b"],
        verdict=parsed["verdict"],
        topic=parsed["topic"],
        severity=parsed["severity"],
        explanation=parsed["explanation"],
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
        print(f"\n--- Requirement {i}: {flag.topic} ({flag.severity}) ---")
        print(f"Verdict: {flag.verdict}")
        print(f"Regulation says: {flag.quote_a}")
        print(f"Vendor says: {flag.quote_b}")
        print(f"Explanation: {flag.explanation}")