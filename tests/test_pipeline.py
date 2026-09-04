"""
Basic tests for the vendor risk checker's non-LLM logic.

These tests deliberately avoid calling ask_model() or Ollama, so they run fast
and don't require the model server to be running. Anyone cloning this repo
should be able to run `pytest` immediately, with no setup beyond `pip install -r requirements.txt`.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingest import chunk_text
from src.models import Flag, parse_model_response, is_flagged, severity_color, highlight_quote


# --- Tests for chunk_text (src/ingest.py) ---

def test_chunk_text_produces_expected_chunk_count():
    text = "A" * 1000  # 1000 characters
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    # start moves by (500 - 50) = 450 each time, so we expect roughly 3 chunks
    assert len(chunks) == 3


def test_chunk_text_respects_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXY"  # 25 characters
    chunks = chunk_text(text, chunk_size=10, overlap=3)
    # last 3 chars of chunk 1 should match first 3 chars of chunk 2
    assert chunks[0][-3:] == chunks[1][:3]


def test_chunk_text_handles_short_text():
    text = "short"
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == "short"


def test_chunk_text_handles_empty_string():
    chunks = chunk_text("", chunk_size=500, overlap=50)
    assert chunks == []


# --- Tests for parse_model_response (src/models.py) ---

def test_parse_model_response_extracts_all_fields():
    sample_response = """TOPIC: Data Encryption
SEVERITY: High
VERDICT: Contradiction Found
QUOTE_A: Vendor shall encrypt all Client customer data at rest and in transit.
QUOTE_B: Data may be temporarily cached in unencrypted form during processing.
PLAIN_EXPLANATION: The contract promises full encryption, but the privacy policy admits an exception."""

    parsed = parse_model_response(sample_response)

    assert parsed["topic"] == "Data Encryption"
    assert parsed["severity"] == "High"
    assert parsed["verdict"] == "Contradiction Found"
    assert "encrypt all Client customer data" in parsed["quote_a"]
    assert "unencrypted form" in parsed["quote_b"]
    assert "contract promises full encryption" in parsed["explanation"]


def test_parse_model_response_handles_missing_fields_gracefully():
    incomplete_response = "VERDICT: Satisfied\nPLAIN_EXPLANATION: Everything checks out."
    parsed = parse_model_response(incomplete_response)

    assert parsed["verdict"] == "Satisfied"
    assert parsed["topic"] == "General"  # default fallback
    assert parsed["quote_a"] == ""        # default fallback


def test_parse_model_response_handles_completely_malformed_text():
    junk = "this is not structured at all"
    parsed = parse_model_response(junk)

    # should not crash, and explanation should fall back to the raw text
    assert parsed["explanation"] == junk
    assert parsed["verdict"] == "Unclear"


# --- Tests for is_flagged (src/models.py) ---

def make_flag(verdict: str) -> Flag:
    """Helper to build a minimal Flag for testing, without needing a real model call."""
    return Flag(
        flag_type="gap",
        source_a="Regulation",
        text_a="some text",
        source_b="vendor_a",
        text_b="some vendor text",
        quote_a="quote a",
        quote_b="quote b",
        verdict=verdict,
        topic="Test Topic",
        severity="Medium",
        explanation="test explanation",
        raw_response="raw"
    )


def test_is_flagged_true_for_gap_found():
    flag = make_flag("Gap Found")
    assert is_flagged(flag) is True


def test_is_flagged_true_for_contradiction_found():
    flag = make_flag("Contradiction Found")
    assert is_flagged(flag) is True


def test_is_flagged_false_for_satisfied():
    flag = make_flag("Satisfied")
    assert is_flagged(flag) is False


def test_is_flagged_false_for_consistent():
    flag = make_flag("Consistent")
    assert is_flagged(flag) is False


def test_is_flagged_case_insensitive():
    flag = make_flag("gap found")  # lowercase
    assert is_flagged(flag) is True


# --- Tests for severity_color (src/models.py) ---

def test_severity_color_high_is_red():
    assert severity_color("High") == "red"


def test_severity_color_medium_is_orange():
    assert severity_color("Medium") == "orange"


def test_severity_color_low_is_blue():
    assert severity_color("Low") == "blue"


def test_severity_color_unknown_defaults_to_gray():
    assert severity_color("Unclear") == "gray"


def test_severity_color_case_insensitive():
    assert severity_color("high") == "red"


# --- Tests for highlight_quote (src/models.py) ---

def test_highlight_quote_wraps_matching_text():
    full_text = "This is a sentence. This part matters. This is another sentence."
    quote = "This part matters."
    result = highlight_quote(full_text, quote)
    assert "**:orange[This part matters.]**" in result


def test_highlight_quote_returns_original_if_quote_not_found():
    full_text = "This is the original text."
    quote = "This sentence does not appear anywhere."
    result = highlight_quote(full_text, quote)
    assert result == full_text


def test_highlight_quote_returns_original_if_quote_is_empty():
    full_text = "Some text here."
    result = highlight_quote(full_text, "")
    assert result == full_text


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])