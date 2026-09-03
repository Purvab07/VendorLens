import ollama

SYSTEM_PROMPT="""
You are a compiance risk assistant. You compare documents, against other documents, or against regulations, to find gaps or contradications.
Rules one must follow:
- Only state problems which you can prove by using reference material or text from the documents uploaded.
- If you are not confident about the answer, then do not guess or hallucinate. Just say that "I don't know".
- Keep answers structured in a specific manner. Do not make if vague or generic.
"""

def ask_model(prompt:str, model:str='llama3.2'):
    response = ollama.chat(
        model=model,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt}
        ]
    )
    return response['message']['content']

if __name__ == "__main__":
    test_prompt = "In one sentence, explain what a vendor risk assessment is."
    print(ask_model(test_prompt))