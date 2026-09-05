# Contributing to VendorLens

Thanks for considering contributing — this started as a small demo project, but bug reports, suggestions, and improvements are genuinely welcome.

## Reporting a bug

Open an issue and include:
- What you expected to happen
- What actually happened (paste the full error/traceback if there is one)
- Steps to reproduce it
- Your OS and Python version

## Suggesting a feature or improvement

Open an issue describing the idea and why it'd be useful. No need for a polished proposal — a rough idea is a fine starting point for a discussion.

## Making a code change

1. Fork the repo and create a branch off `main`
2. Make your change
3. Run the test suite to make sure nothing broke:
   ```bash
   pip install pytest
   pytest tests/test_pipeline.py -v
   ```
4. If you added new logic, add a test for it where reasonable (see `tests/test_pipeline.py` for examples — tests there avoid needing Ollama running, so keep new tests fast and dependency-free where possible)
5. Open a pull request describing what changed and why

## Local development setup

See the [Setup](README.md#setup) section of the README for full instructions. In short:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2
ollama serve   # keep running in a separate terminal
```

## Project structure

See the [Project structure](README.md#project-structure) section of the README for an overview of what lives where.

## Known limitations worth knowing before contributing

- Text chunking is by fixed character count, not sentence-aware — a good first improvement if you're looking for something meaningful to work on
- The local model occasionally doesn't quote source text verbatim, which affects the quote-highlighting feature
- No support yet for `.docx` files, only `.txt` and `.pdf`

## Code of conduct

Be respectful and constructive. Disagreements about implementation are fine; personal attacks aren't.