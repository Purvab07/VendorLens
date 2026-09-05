# VendorLens

A small AI-powered tool that checks a vendor's paperwork two ways: whether it actually satisfies the regulations it's supposed to follow, and whether the vendor's own documents agree with each other. Built as a compact demo of the kind of compliance-review product [Kobalt Labs](https://www.kobaltlabs.com/) builds for banks and fintechs.

Every finding comes with the exact sentence it's based on and a plain-language explanation — not just a verdict, since an unexplained AI flag isn't useful to a compliance reviewer.

> **Note:** This is an independent educational/demo project inspired by Kobalt Labs' public product description. It is not affiliated with, endorsed by, or built using any proprietary information from Kobalt Labs.

## What it checks

**📋 Gap Coverage** — compares a vendor's documents against real regulation text and flags anything the vendor's paperwork doesn't actually cover.
> *Example: a regulation requires acknowledging complaints within 15 days; the vendor's contract only promises to forward complaints internally within 5 days — a different, weaker commitment.*

**🔍 Contradiction Check** — compares a vendor's own documents against each other and flags inconsistencies.
> *Example: the contract promises full encryption of customer data; the privacy policy admits data is sometimes cached unencrypted.*

See [`docs/example_walkthrough.md`](docs/example_walkthrough.md) for a full worked example with real findings.

## How it works

```
Documents (contracts, policies, regulations)
        │
        ▼
   Ingest & embed  (chunk text, store as searchable vectors)
        │
   ┌────┴────┐
   ▼         ▼
Gap        Contradiction
Coverage    Check
   │         │
   └────┬────┘
        ▼
LLM reasoning (cites exact source sentences + confidence)
        │
        ▼
  Risk dashboard
```

Everything runs locally via [Ollama](https://ollama.com) (Llama 3.2, 3B) — no API costs, no data leaves your machine. The architecture is built so swapping in a stronger model (e.g. Claude) is a one-line change.

## Setup

**1. Install Ollama and pull the model**
```bash
brew install ollama
ollama pull llama3.2
```

**2. Create a virtual environment and install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Start Ollama's server** (keep this running in its own terminal tab)
```bash
ollama serve
```

## Running it

**Start the dashboard:**
```bash
streamlit run app/dashboard.py
```
This opens a browser page at `http://localhost:8501`.

In the sidebar:
1. Give the vendor a name
2. Upload a regulation file (`.txt`/`.pdf`) or paste a public Google Doc link
3. Upload the vendor's documents (`.txt`/`.pdf`, multiple files at once) or paste a Google Doc link
4. Click **Upload & Run analysis**

Results appear in two tabs — Gap Coverage and Contradictions — each finding shown as a card with a topic, severity, plain-language explanation, and the exact quoted sentences involved.

**Or run the checks directly from the terminal**, useful for quick testing:
```bash
python -m src.gap_coverage
python -m src.contradiction_check
```

**Run the test suite:**
```bash
pip install pytest
pytest tests/test_pipeline.py -v
```
These tests cover chunking, response parsing, and helper logic, and don't require Ollama running. Full pipeline testing (the two commands above) does require Ollama running locally.

## Project structure

```
├── app/
│   └── dashboard.py          # Streamlit UI
├── src/
│   ├── ingest.py              # loads & chunks text, PDFs, Google Docs
│   ├── embed.py                # stores/searches chunks via ChromaDB
│   ├── reasoning.py            # calls the local LLM
│   ├── models.py               # shared Flag structure + parsing helpers
│   ├── gap_coverage.py         # vendor vs. regulation
│   └── contradiction_check.py  # vendor doc vs. vendor doc
├── data/
│   ├── regulations/             # sample regulation text
│   └── vendors/vendor_a/        # sample mock vendor documents
├── docs/
│   └── example_walkthrough.md   # worked example with real findings
├── tests/
│   └── test_pipeline.py         # unit tests (no Ollama required)
└── load_vendor_a.py            # quick script to reload test data
```

## Known limitations

- Text is chunked by a fixed character count rather than by sentence, which can occasionally cut a chunk mid-word. Doesn't affect the model's reasoning meaningfully, but is a rough edge.
- Quoted "exact sentences" rely on a small (3B parameter) local model, which can occasionally paraphrase slightly instead of quoting verbatim. When that happens, the UI falls back to showing the full excerpt without highlighting.
- Google Doc support works only for documents shared as "Anyone with the link can view," since it uses Google's public export endpoint rather than full Drive API authentication.
- This is a proof-of-concept, not a production system — mock data, no user auth, no persistence beyond the local Chroma database.

## Why this project

Kobalt Labs' product ingests vendor documents and internal policies, checks them against regulations, and tracks risk over time. This project builds a small working version of that core loop — plus a feature (contradiction checking) that extends it: verifying a vendor's documents are internally consistent with each other, not just individually compliant with the law.

## Contributing

Contributions, bug reports, and suggestions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT — see [LICENSE](LICENSE) for details.
