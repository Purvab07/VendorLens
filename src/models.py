from dataclasses import dataclass
import re


@dataclass
class Flag:
    """A single finding, whether from gap coverage or contradiction checking."""
    flag_type: str
    source_a: str
    text_a: str
    source_b: str
    text_b: str
    quote_a: str
    quote_b: str
    verdict: str
    topic: str
    severity: str
    explanation: str
    raw_response: str


def parse_model_response(response: str) -> dict:
    """Pulls TOPIC, SEVERITY, VERDICT, QUOTE_A, QUOTE_B, and PLAIN_EXPLANATION out of the model's response."""
    def extract(field_name, text, default=""):
        match = re.search(rf"{field_name}:\s*(.+)", text)
        return match.group(1).strip() if match else default

    topic = extract("TOPIC", response, "General")
    severity = extract("SEVERITY", response, "Unclear")
    verdict = extract("VERDICT", response, "Unclear")
    quote_a = extract("QUOTE_A", response, "")
    quote_b = extract("QUOTE_B", response, "")

    explanation_match = re.search(r"PLAIN_EXPLANATION:\s*(.+)", response, re.DOTALL)
    explanation = explanation_match.group(1).strip() if explanation_match else response.strip()

    return {
        "topic": topic,
        "severity": severity,
        "verdict": verdict,
        "quote_a": quote_a,
        "quote_b": quote_b,
        "explanation": explanation
    }


def is_flagged(flag: Flag) -> bool:
    """True if this finding represents an actual problem worth surfacing."""
    problem_verdicts = {"gap found", "contradiction found"}
    return flag.verdict.strip().lower() in problem_verdicts


def severity_color(severity: str) -> str:
    """Maps a severity level to a color for the UI."""
    s = severity.strip().lower()
    if s == "high":
        return "red"
    elif s == "medium":
        return "orange"
    elif s == "low":
        return "blue"
    return "gray"


def highlight_quote(full_text: str, quote: str) -> str:
    """Wraps the quoted sentence in bold highlighted markdown within the full excerpt, if found."""
    if not quote or quote not in full_text:
        return full_text
    return full_text.replace(quote, f"**:orange[{quote}]**")