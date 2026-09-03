from src.embed import get_collections, search
from src.reasoning import ask_model

def get_all_chunks(collection_name:str):
    collection = get_collections(collection_name)
    return collection.get()

def build_gap_prompt(regulation_text:str,vendor_text:str) ->str:
    return f"""Regulation requirement:
    \"\"\"{regulation_text}\"\"\"

    Vendor document excerpt (most relevant section found):
    \"\"\"{vendor_text}\"\"\"

    Question: Does the vendor document excerpt satisfy this regulation requirement?
    Answer in this exact format:
    VERDICT: <Satisfied / Gap Found / Unclear>
    EXPLANATION: <one or two sentences, referencing the specific text that supports your verdict>
    """

def check_requirement(regulation_text: str, vendor_collection_name: str) -> dict:
    match = search(query=regulation_text, collection_name=vendor_collection_name, n_results=1)
    vendor_text = match["documents"][0][0] if match["documents"][0] else "No relevant vendor text found."

    prompt = build_gap_prompt(regulation_text, vendor_text)
    response = ask_model(prompt)

    return {
        "requirement": regulation_text,
        "matched_vendor_text": vendor_text,
        "model_response": response
    }

def run_gap_analysis(vendor_collection_name: str, regulation_collection_name: str = "regulations") -> list[dict]:
    regulations = get_all_chunks(regulation_collection_name)
    results = []

    for reg_text in regulations["documents"]:
        result = check_requirement(reg_text, vendor_collection_name)
        results.append(result)

    return results

if __name__ == "__main__":
    findings = run_gap_analysis(vendor_collection_name="vendor_a")

    for i, finding in enumerate(findings, start=1):
        print(f"\n--- Requirement {i} ---")
        print(f"Regulation: {finding['requirement'][:150]}...")
        print(finding["model_response"])