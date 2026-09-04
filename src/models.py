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
    verdict: str
    explanation: str
    raw_response: str


def parse_model_response(response: str) -> tuple[str, str]:
    """Pulls the VERDICT and EXPLANATION out of the model's structured text response."""
    verdict_match = re.search(r"VERDICT:\s*(.+)", response)
    explanation_match = re.search(r"EXPLANATION:\s*(.+)", response, re.DOTALL)

    verdict = verdict_match.group(1).strip() if verdict_match else "Unclear"
    explanation = explanation_match.group(1).strip() if explanation_match else response.strip()

    return verdict, explanation


def is_flagged(flag: Flag) -> bool:
    """True if this finding represents an actual problem worth surfacing."""
    problem_verdicts = {"gap found", "contradiction found"}
    return flag.verdict.strip().lower() in problem_verdicts