from dataclasses import dataclass
import re


@dataclass
class Flag:
    """A single finding, whether from gap coverage or contradiction checking."""
    flag_type: str        # "gap" or "contradiction"
    source_a: str          # e.g. regulation label, or first vendor document
    text_a: str             # the actual excerpt from source_a
    source_b: str          # e.g. vendor document label, or second vendor document
    text_b: str             # the actual excerpt from source_b
    verdict: str            # e.g. "Satisfied", "Gap Found", "Contradiction Found", "Consistent", "Unclear"
    explanation: str        # the model's reasoning
    raw_response: str       # the full, unparsed model output, kept for reference


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