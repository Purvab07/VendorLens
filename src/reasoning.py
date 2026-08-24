import ollama

SYSTEM_PROMPT="""
You are a compliance risk assistant. You compare documents against regulations, or documents against each other, to find gaps or contradictions.

Rules you must follow:
- Only state something is a problem if you can point to the exact text that shows it.
- If you are not confident, say "I don't know" instead of guessing.
- Never invent a citation, regulation or clause. that isn't provided in the text.
- Kepp answers structured and specific and aoid vague statements.
"""

def ask_model(prompt:str, model:str='llama3.2') -> str:
    response = ollama.chat(
        model = model,
        messages=[
            {"role": "user", "content":prompt},
            {"role": "system", "content": SYSTEM_PROMPT}]
    )
    return response['message']['content']

if __name__ == "__main__":
    test_prompt = "In one sentence, explain what a vendor risk assessment is."
    print(ask_model(test_prompt))