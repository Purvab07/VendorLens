from src.embed import get_collections
from src.reasoning import ask_model
from src.models import Flag, parse_model_response


def get_chunks_by_source(collection_name: str) -> dict:
    """Groups all chunks in a collection by which source file they came from."""
    collection = get_collections(collection_name)
    all_data = collection.get()

    grouped = {}
    for doc_text, metadata in zip(all_data["documents"], all_data["metadatas"]):
        source = metadata["source"]
        grouped.setdefault(source, []).append(doc_text)

    return grouped


def build_contradiction_prompt(source_a: str, text_a: str, source_b: str, text_b: str) -> str:
    return f"""Document A ({source_a}):
\"\"\"{text_a}\"\"\"

Document B ({source_b}):
\"\"\"{text_b}\"\"\"

Question: Do these two excerpts, from the same vendor, contradict each other or say something inconsistent on the same topic?
Answer in this exact format:
VERDICT: <Consistent / Contradiction Found / Unclear>
EXPLANATION: <one or two sentences, quoting or referencing the specific conflicting statements>
"""


def check_pair(source_a: str, text_a: str, source_b: str, text_b: str) -> Flag:
    prompt = build_contradiction_prompt(source_a, text_a, source_b, text_b)
    response = ask_model(prompt)
    verdict, explanation = parse_model_response(response)

    return Flag(
        flag_type="contradiction",
        source_a=source_a,
        text_a=text_a,
        source_b=source_b,
        text_b=text_b,
        verdict=verdict,
        explanation=explanation,
        raw_response=response
    )


def run_contradiction_check(vendor_collection_name: str) -> list[Flag]:
    grouped = get_chunks_by_source(vendor_collection_name)
    sources = list(grouped.keys())
    results = []

    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            source_a, source_b = sources[i], sources[j]
            text_a = grouped[source_a][0]
            text_b = grouped[source_b][0]

            result = check_pair(source_a, text_a, source_b, text_b)
            results.append(result)

    return results


if __name__ == "__main__":
    findings = run_contradiction_check(vendor_collection_name="vendor_a")

    for i, flag in enumerate(findings, start=1):
        print(f"\n--- Comparison {i}: {flag.source_a} vs {flag.source_b} ---")
        print(f"Verdict: {flag.verdict}")
        print(f"Explanation: {flag.explanation}")