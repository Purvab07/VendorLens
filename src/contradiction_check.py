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

You are explaining this to someone with no legal or compliance background.
Answer in this exact format, with no extra text before or after:

TOPIC: <a short 2-4 word category, e.g. "Data Encryption">
SEVERITY: <High / Medium / Low — how serious this inconsistency would be>
VERDICT: <Consistent / Contradiction Found / Unclear>
QUOTE_A: <copy the exact sentence from Document A that is the source of the inconsistency — word for word, no paraphrasing>
QUOTE_B: <copy the exact sentence from Document B that conflicts with it — word for word, no paraphrasing>
PLAIN_EXPLANATION: <1-2 sentences in simple, everyday language explaining what each document actually says and why the difference matters>
"""


def check_pair(source_a: str, text_a: str, source_b: str, text_b: str) -> Flag:
    prompt = build_contradiction_prompt(source_a, text_a, source_b, text_b)
    response = ask_model(prompt)
    parsed = parse_model_response(response)

    return Flag(
        flag_type="contradiction",
        source_a=source_a,
        text_a=text_a,
        source_b=source_b,
        text_b=text_b,
        quote_a=parsed["quote_a"],
        quote_b=parsed["quote_b"],
        verdict=parsed["verdict"],
        topic=parsed["topic"],
        severity=parsed["severity"],
        explanation=parsed["explanation"],
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
        print(f"\n--- Comparison {i}: {flag.source_a} vs {flag.source_b} ({flag.topic}, {flag.severity}) ---")
        print(f"Verdict: {flag.verdict}")
        print(f"{flag.source_a} says: {flag.quote_a}")
        print(f"{flag.source_b} says: {flag.quote_b}")
        print(f"Explanation: {flag.explanation}")